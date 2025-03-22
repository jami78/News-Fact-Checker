from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.auth.auth import get_current_user
from app.db.crud.creative_writing import get_creative_writing_doc  
from app.utils.helpers import BASE_DIR

router = APIRouter()

@router.get("/fact-check/creative-writing/")
async def download_creative_writing(current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    """ Retrieves the latest creative writing DOCX file for the user. """
    absolute_path = get_creative_writing_doc(db, current_user)
    return FileResponse(absolute_path, media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document", filename="creative_report.docx")
