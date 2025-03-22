from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from typing import Optional, List
import os
from app.schemas.factcheck import FactCheckRequest, FactCheckResponse
from app.llm.agents import agent
from app.llm.llm_services import llm_openai
from app.utils.helpers import generated_files, get_user_folder
from app.services.doc_to_pdf import markdown_to_docx, convert_docx_to_pdf
from app.services.drive_upload import upload_docx_to_drive
from app.services.generate_report import generate_report
from langchain.document_loaders import UnstructuredURLLoader, PyMuPDFLoader
from langchain.output_parsers import PydanticOutputParser
from app.schemas.factcheckurl import FactCheckURLs
from app.config import get_settings
import uuid
from sqlalchemy.orm import Session
from app.prompts.fact_check_prompt import get_fact_check_prompt
from app.prompts.creative_writing_prompt import get_creative_writing_prompt
from app.auth.auth import get_current_user
from app.core.database import get_db
from app.db.crud.fact_check import store_fact_check_data
from app.utils.extract_claim import extract_claim_text  
from app.utils.parse_fact_check import parse_fact_check_response
parser = PydanticOutputParser(pydantic_object=FactCheckURLs)
settings = get_settings()
drive_folder_link = settings.DRIVE_FOLDER_LINK      
# Create a router for fact_check endpoints  
router = APIRouter()

@router.post("/fact-check/", response_model=FactCheckResponse)
async def fact_check(
    request: FactCheckRequest = Depends(),
    pdf_file: Optional[UploadFile] = File(None),
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)   #  Requires authentication
):
    try:
        #  Generate a unique session ID
        session_id = str(uuid.uuid4())  

        claim = await extract_claim_text(request.claim, request.url, pdf_file, current_user)
        #  Run AI Fact-Checking Process
        user_query = claim  
        fact_check_data = agent.invoke({"input": claim})["output"]

        #  Ensure proper formatting
        parsed_fact_check = parse_fact_check_response(fact_check_data)

        # Extract URLs for news articles
        urls_to_check = parsed_fact_check.urls

        # Step 2: Fetch news articles from extracted URLs
        loader = UnstructuredURLLoader(urls=urls_to_check)
        documents = loader.load()
        news_texts = [doc.page_content for doc in documents]
        
        fact_check_prompt = get_fact_check_prompt(claim, news_texts)
        fact_check_report = llm_openai.invoke(fact_check_prompt).content

        formatted_report = generate_report(fact_check_report, urls_to_check)

        #  Store reports in user-specific directory
        user_folder = get_user_folder(current_user)
        docx_filename = os.path.join(user_folder, "fact_check_report.docx")
        creative_docx_filename = os.path.join(user_folder, "creative_report.docx")

        markdown_to_docx(formatted_report, docx_filename)
        
        # ✅ Generate PDF
        pdf_file_url = convert_docx_to_pdf(docx_filename)

        # Upload Google Docs to Drive
        google_doc_url = upload_docx_to_drive(docx_filename, drive_folder_link)

        #  Generate Creative Writing (Op-Ed)
        creative_prompt = get_creative_writing_prompt(formatted_report, urls_to_check)
        creative_response = llm_openai.invoke(creative_prompt).content
        markdown_to_docx(creative_response, creative_docx_filename)

        store_fact_check_data(
            db=db,
            session_id=session_id,
            username=current_user,
            user_query=user_query,
            formatted_report=formatted_report,
            google_doc_url=google_doc_url,
            pdf_file_url=pdf_file_url,
            creative_docx_filename=creative_docx_filename
        )

        # Return response with session ID and generated files
        return FactCheckResponse(
            session_id=session_id,  
            claim=claim,
            fact_check_result=formatted_report,
            urls=urls_to_check
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
