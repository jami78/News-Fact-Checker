from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_id = Column(String, nullable=False)
    username = Column(String, ForeignKey("users.username"), nullable=False)  # ✅ Foreign key reference
    user_input = Column(Text, nullable=False)
    ai_response = Column(Text, nullable=False)
    google_doc_url = Column(String, nullable=True)
    pdf_file_url = Column(String, nullable=True)
    creative_docx_file = Column(String, nullable=True)
    timestamp = Column(DateTime, default=func.now())
    __table_args__ = {'extend_existing': True}
    # Relationship with User
    user = relationship("User", back_populates="chat_history", foreign_keys=[username])

