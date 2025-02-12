import streamlit as st
from dotenv import load_dotenv
from langchain.agents import initialize_agent, AgentType
from langchain.tools import Tool
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain.tools import DuckDuckGoSearchRun, TavilySearchResults
from langchain_community.utilities import GoogleSerperAPIWrapper
from pydantic import BaseModel, HttpUrl, Field
from langchain.output_parsers import PydanticOutputParser
from langchain.schema import SystemMessage
from langchain.document_loaders import UnstructuredURLLoader
from datetime import datetime
import textwrap
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import google.auth
from google.oauth2 import service_account
from googleapiclient.discovery import build
import google.generativeai as genai
import os
import re
load_dotenv(dotenv_path= '/teamspace/studios/this_studio/env.txt')
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")  

GROQ= os.getenv("GROQ_API_KEY")

# Configure the genai library with your API key
genai.configure(api_key=GOOGLE_API_KEY)
llm_groq= ChatGroq(model='llama3-70b-8192', api_key= GROQ)
llm_gemini = genai.GenerativeModel(model_name="gemini-2.0-flash")


# Search functions
def google_search_tool(query):
    return GoogleSerperAPIWrapper().run(query)

def duckduckgo_tool(query):
    return DuckDuckGoSearchRun().run(query)

def tavily_tool(query):
    return TavilySearchResults(search_depth="advanced", include_answer=True, include_images=True).invoke(query)

# Wrap tools in Tool class
tools = [
    Tool(name="Google Search", func=google_search_tool, description="Search Google for news"),
    Tool(name="DuckDuckGo Search", func=duckduckgo_tool, description="Search DuckDuckGo for news"),
    Tool(name="Tavily Search", func=tavily_tool, description="Search Tavily for related sources")
]

# Initialize the agent
agent = initialize_agent(
    tools=tools,
    llm=llm_groq,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# Define structured output using Pydantic
class FactCheckURLs(BaseModel):
    claim: str = Field(description="The claim being fact-checked.")
    urls: list[HttpUrl] = Field(description="A list of URLs that contain relevant news articles.")

# Initialize output parser
parser = PydanticOutputParser(pydantic_object=FactCheckURLs)

# Function to generate the fact-check report
def generate_report(fact_check_result, urls):
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report_header = f"""
{"#" * 50}
Fact-Check Report
Date: {current_date}
{"#" * 50}
"""
    claim_section = f"""
## Claim:
{user_claim}
"""
    fact_check_section = f"""
## Fact-Check Findings:
{fact_check_result}
"""
    sources_section = f"""
## Sources:
The following sources were used to verify the claim:
"""
    for url in urls:
        sources_section += f"- {url}\n"

    full_report = report_header + claim_section + fact_check_section + sources_section
    return full_report

# Function to save the report as a PDF
def save_report_as_pdf(formatted_report, filename="fact_check_report.pdf"):
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    c.setFont("Helvetica", 10)
    y_position = height - 40
    for line in formatted_report.split("\n"):
        if y_position < 40:
            c.showPage()
            c.setFont("Helvetica", 10)
            y_position = height - 40
        c.drawString(50, y_position, line.strip())
        y_position -= 15
    c.save()
    return filename

# Load credentials
def get_google_services():
    creds = service_account.Credentials.from_service_account_file(
        "/teamspace/studios/this_studio/fact-checker-450613-deb87d989f62.json",
        scopes=["https://www.googleapis.com/auth/documents", "https://www.googleapis.com/auth/drive.file"]
    )
    docs_service = build("docs", "v1", credentials=creds)
    drive_service = build("drive", "v3", credentials=creds)  # Drive API
    return docs_service, drive_service

# Extract Folder ID from full Google Drive folder link
def extract_folder_id(drive_link):
    match = re.search(r"drive\.google\.com/drive/folders/([a-zA-Z0-9_-]+)", drive_link)
    return match.group(1) if match else None

# Create and write to a Google Doc
def create_google_doc(report_text):
    docs_service, drive_service = get_google_services()

    # Create a new document
    doc = docs_service.documents().create(body={"title": "Fact-Check Report"}).execute()
    doc_id = doc["documentId"]

    # Write content
    requests = [{"insertText": {"location": {"index": 1}, "text": report_text}}]
    docs_service.documents().batchUpdate(documentId=doc_id, body={"requests": requests}).execute()

    return doc_id

# Upload the doc to the shared folder
def move_doc_to_folder(doc_id, drive_link):
    _, drive_service = get_google_services()

    # Extract Folder ID
    folder_id = extract_folder_id(drive_link)
    if not folder_id:
        return "Invalid Google Drive folder link."

    # Move the document to the shared folder
    file_metadata = {"parents": [folder_id]}
    drive_service.files().update(fileId=doc_id, addParents=folder_id, removeParents="root", fields="id, parents").execute()

    return f"https://docs.google.com/document/d/{doc_id}"

# ✅ User provides the full Google Drive folder link
drive_folder_link = "https://drive.google.com/drive/folders/1kPc5b41KpJur_pTKLXGLlCB2IjD5-eC2?dmr=1&ec=wgc-drive-hero-goto"  


# Streamlit interface
st.title("📰 Fact-Checking Tool")
st.write("Enter a claim to fact-check and get a detailed report.")

# User input for the claim
user_claim = st.text_input("Enter the claim to fact-check:",)
if st.button("Fact-Check"):
    with st.spinner("Analyzing the claim..."):
        try:
            # Step 1: Retrieve relevant news sources
            query = f"Find credible news sources related to this claim: {user_claim}.{parser.get_format_instructions()}"
            fact_check_data = agent.run(query)

            # Step 2: Parse response
            fact_check_data = parser.parse(fact_check_data)
            try:
                if not isinstance(fact_check_data, str):  # Check if it's not a string
                    fact_check_data = fact_check_data.model_dump_json()  # Convert to JSON if not a string
                fact_check_data = parser.parse(fact_check_data)  # Parse the data
            except Exception as e:
                print(f"Error parsing response: {e}")
                print(f"Raw response: {fact_check_data}")
                print(f"Expected format: {parser.get_format_instructions()}")
                raise e 
            # Step 3: Load full content of the URLs
            urls_to_check = fact_check_data.urls
            loader = UnstructuredURLLoader(urls=urls_to_check)
            documents = loader.load()
            news_texts = [doc.page_content for doc in documents]

            # Step 4: Fact-check using GPT-4
            fact_check_prompt = f"""
            Claim: "{user_claim}"

            Below are news articles related to the claim:

            {news_texts[:2000]}  # Limit to avoid token overflow

            Analyze the claim using these sources:
            - Identify which parts are **true, false, or uncertain**.
            - Highlight contradictions between sources.
            - Reference sources when making a judgment.
            """
            fact_check_report = llm_gemini.generate_content(fact_check_prompt)
            fact_check_report= fact_check_report.text
            # Log the raw response object in Streamlit
            #st.write("Raw Fact-Check Response:")
            #st.write(fact_check_report)

            # Step 5: Generate report
            formatted_report = generate_report(fact_check_report, fact_check_data.urls)
            # Display report
            st.subheader("Fact-Check Report")
            st.write(formatted_report)

            # Step 6: User selects PDF or Google Doc
            st.subheader("Download Report")

            # PDF Download Button
            pdf_filename = save_report_as_pdf(formatted_report)
            with open(pdf_filename, "rb") as pdf_file:
                st.download_button(
                    label="📄 Download Report as PDF",
                    data=pdf_file,
                    file_name=pdf_filename,
                    mime="application/pdf"
                )

            # Google Docs Upload & Open Button
            doc_id = create_google_doc(formatted_report)  # Create Google Doc
            google_doc_url = move_doc_to_folder(doc_id, drive_folder_link)  # Move to a folder

            # Button to open the Google Doc
            st.markdown(
                f'<a href="{google_doc_url}" target="_blank">'
                f'<button style="padding:10px 15px; background-color:#008CBA; color:white; border:none; border-radius:5px; cursor:pointer; width:100%;">'
                f'📄 Open Report in Google Docs</button></a>',
                unsafe_allow_html=True
            )
        except Exception as e:
            st.error(f"An error occurred: {e}")
            st.write("Raw response from the agent:", formatted_report)
