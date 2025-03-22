
# **News Fact-Checker API**
This project is a **Fact-Checking System** that verifies the credibility of a given claim against reliable online sources. It utilizes **LLMs from Groq and Gemini**, along with **Google Drive API for document storage**.

---
## **🏗️ Structure**


├── app
│   │── config.py
│   │── __init__.py
│   │
│   ├── api
│   │   │── __init__.py
│   │   │
│   │   ├── v1
│   │   │   │── auth.py
│   │   │   │── creative_writing.py
│   │   │   │── documents.py
│   │   │   │── fact_check.py
│   │   │   │── history.py
│   │   │   │── __init__.py
│   │
│   ├── auth
│   │   │── auth.py
│   │   │── __init__.py
│   │
│   ├── core
│   │   │── database.py
│   │   │── __init__.py
│   │
│   ├── db
│   │   │── __init__.py
│   │   │
│   │   ├── crud
│   │   │   │── chat_history.py
│   │   │   │── creative_writing.py
│   │   │   │── documents.py
│   │   │   │── fact_check.py
│   │   │   │── users.py
│   │   │   │── __init__.py
│   │
│   ├── llm
│   │   │── agents.py
│   │   │── llm_services.py
│   │   │── __init__.py
│   │
│   ├── models
│   │   │── chat_history.py
│   │   │── users.py
│   │   │── __init__.py
│   │
│   ├── prompts
│   │   │── agent_prompt.py
│   │   │── creative_writing_prompt.py
│   │   │── fact_check_prompt.py
│   │   │── __init__.py
│   │
│   ├── schemas
│   │   │── chathistory.py
│   │   │── factcheck.py
│   │   │── factcheckurl.py
│   │   │── __init__.py
│   │
│   ├── services
│   │   │── doc_to_pdf.py
│   │   │── drive_upload.py
│   │   │── generate_report.py
│   │   │── __init__.py
│   │
│   ├── utils
│   │   │── extract_claim.py
│   │   │── helpers.py
│   │   │── parse_fact_check.py
│   │   │── __init__.py
│
├── data
│   └── uploads
│       └── lionelmessi
│           │── creative_report.docx
│           │── fact_check_report.docx
│           │── fact_check_report.pdf
│
├── .env
├── .gitkeep
├── chat_history.db
├── fact-checker-450613-deb87d989f62.json
├── main.py
├── README.md
├── requirements.txt
└── Workflow.png

---

## **🚀 Features**
✅ **AI-Powered Fact-Checking**: Uses the advanced **GPT-4o**
✅ **Credible Source Extraction**: Searches the web and evaluates the claim against top sources  
✅ **Report Generation**: Creates a **detailed fact-checking report**  
✅ **Document Storage**: Saves the report as **PDF & DOCX**, uploads to **Google Drive**  
✅ **Creative Writing**: Generates an **op-ed style** explanation of the claim  

---

## **⚙️ Technology Stack**
- **FastAPI** (Backend Framework)
- **GPT-4o** (Fact-checking and report generation agent)
- **Google Drive API** (For document uploads)
- **LangChain** (LLM interaction & source retrieval)

---

## **📂 API Endpoints**
| **Method** | **Endpoint** | **Description** |
|------------|-------------|----------------|
| `POST` | `/fact-check/` | Generates a fact-checking report for a given claim, URL, or PDF |
| `GET` | `/fact-check/document/google-docx` | Converts the report to a google doc and provides a url |
| `GET` | `/fact-check/document/pdf` | Converts the report to PDF |
| `GET` | `/fact-check/creative-writing/` | Generates an **op-ed style** explanation of the claim |
| `GET` | `/chat-history/` | Shows the chat history of a user |
| `GET` | `/register/` | Registers a new user |
| `GET` | `/token/` | Login endpoint for existing users |

---

## **📥 Installation & Setup**
### **1️⃣ Clone the Repository**
```bash
git clone https://github.com/Liberate-Labs/AI-Intern-Assignments.git
cd AI-Intern-Assignments/news-fact-checker[jami]
```

### **2️⃣ Set Up a Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate      # Windows
```

### **3️⃣ Install Dependencies**
```bash
pip install -r requirements.txt
```

---

## **🔑 .env File Configuration**
Create a `.env` file in the root directory and add the following API keys:

```
GROQ_API_KEY=your_groq_api_key_here
GEMINI_API_KEY=your_google_api_key_here
OPENAI_API_KEY= your_openai_api_key_here
DRIVE_FOLDER_LINK=https://drive.google.com/drive/folders/YOUR_FOLDER_ID
```
✅ **Create a new Google drive folder for google drive upload and replace `YOUR_FOLDER_ID` with the Google Drive folder.**

---

## Create a Google service ID and pass the credentials in services/drive_upload.py
## **📁 Setting Up Google Cloud Service Account for Drive Uploads**
To enable **automatic document uploads to Google Drive**, you need to set up a **Google Cloud Service Account**.

### **1️⃣ Create a Google Cloud Project**
- Go to **[Google Cloud Console](https://console.cloud.google.com/)**.
- Create a new project.

### **2️⃣ Enable the Google Drive API**
- In the **Google Cloud Console**, go to **APIs & Services > Library**.
- Search for **Google Drive API** and **enable it**.

### **3️⃣ Generate a Service Account**
- Go to **IAM & Admin > Service Accounts**.
- Click **"Create Service Account"**.
- Assign it **Editor** and **Drive API roles**.
- Click **"Create Key"** (Select JSON).
- **Download the JSON file** and rename it as `google_service_account.json`.
- Move it to your project root folder.

✅ **Now your service account can upload documents to Google Drive!**  

---

## **🚀 Running the API**
Start the FastAPI server:
```bash
uvicorn app.main:app --reload
```
✅ **Now the API is running at**: `http://127.0.0.1:8000`

To test the API, open:
```bash
http://127.0.0.1:8000/docs
```
✅ **Swagger UI will display all available endpoints.**

---
