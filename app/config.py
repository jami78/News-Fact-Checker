import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv



class Settings(BaseSettings):
    """Application Configuration Settings"""
    GROQ_API_KEY: str
    SERPER_API_KEY: str
    OPENAI_API_KEY: str
    TAVILY_API_KEY: str
    GEMINI_API_KEY: str
    DRIVE_FOLDER_LINK: str = "https://drive.google.com/drive/folders/1kPc5b41KpJur_pTKLXGLlCB2IjD5-eC2?dmr=1&ec=wgc-drive-hero-goto"
    SECRET_KEY: str
    ALGORITHM: str

    class Config:
        env_file = ".env" 

# Singleton function to get settings
def get_settings() -> Settings:
    load_dotenv(override=True)
    return Settings()


