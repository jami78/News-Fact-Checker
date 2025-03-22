from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.auth.auth import get_current_user
from app.db.crud.documents import get_pdf_file, get_google_doc_url


router = APIRouter()

@router.get("/fact-check/pdf/")
async def get_pdf_file_url(current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    """ Retrieves the latest fact-checking PDF file for the user. """
    absolute_path = get_pdf_file(db, current_user)
    return FileResponse(absolute_path, media_type="application/pdf", filename="fact_check_report.pdf")

@router.get("/fact-check/google-docx/")
async def get_google_doc_url_endpoint(current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    """ Retrieves the latest Google Docs URL for the user. """
    google_doc_url = get_google_doc_url(db, current_user)
    return {"google_doc_url": google_doc_url}
