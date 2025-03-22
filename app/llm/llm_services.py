import google.generativeai as genai
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os
from langchain_openai import ChatOpenAI
from app.config import get_settings

settings = get_settings()
GOOGLE_API_KEY = settings.GEMINI_API_KEY
GROQ_API_KEY = settings.GROQ_API_KEY
OPENAI_API_KEY = settings.OPENAI_API_KEY

# 🔹 Configure Google Gemini API
genai.configure(api_key=GOOGLE_API_KEY)
llm_gemini = genai.GenerativeModel(model_name="gemini-2.0-flash")

# 🔹 Configure Groq API (LLaMA 3 or Mixtral)
llm_groq = ChatGroq(model='llama3-70b-8192', api_key=GROQ_API_KEY, temperature=0.2)


llm_openai = ChatOpenAI(
    model_name="gpt-4o",
    openai_api_key=OPENAI_API_KEY,
    temperature=0.2
)