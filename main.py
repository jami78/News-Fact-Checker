import streamlit as st
from dotenv import load_dotenv
from langchain.agents import initialize_agent, AgentType
from langchain.tools import Tool
from langchain_groq import ChatGroq
from langchain.tools import DuckDuckGoSearchRun, TavilySearchResults, ArxivQueryRun
from langchain_community.utilities import GoogleSerperAPIWrapper
from pydantic import BaseModel, HttpUrl, Field
from langchain.output_parsers import PydanticOutputParser
from langchain.schema import SystemMessage
from langchain.document_loaders import UnstructuredURLLoader
import textwrap
import google.auth
import google.generativeai as genai
import os
from datetime import datetime
from doc_to_pdf import convert_docx_to_pdf
from doc_to_pdf import markdown_to_docx
from drive_upload import upload_docx_to_drive
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

# Define tools
def arxiv_tool(query):
    return ArxivQueryRun().run(query)

# Wrap tools in Tool class
tools = [
    Tool(name="Google Search", func=google_search_tool, description="Search Google for news"),
    Tool(name="DuckDuckGo Search", func=duckduckgo_tool, description="Search DuckDuckGo for news"),
    Tool(name="Tavily Search", func=tavily_tool, description="Search Tavily for related sources"),
    Tool(name="ArXiv Research Papers", func=arxiv_tool, description="Search academic papers from ArXiv")
]

# Initialize the agent
agent = initialize_agent(
    tools=tools,
    llm=llm_groq,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)
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

def generate_creative_writing_from_report(report, formatted_sources):
    creative_prompt = f"""
    Here is the fact-checking report:

    {report}

    Based on the above report, write an op-ed that conveys the contents in a rather human way. The op-ed should feel informative and engaging, incorporating themes from the fact-check. Make it at least 600 words.
    At the end, include a **'Sources'** section listing the URLs of the references used for fact-checking.

    ---

    **Sources:**
    {formatted_sources}
    """
    creative_response = llm_gemini.generate_content(creative_prompt)
    creative_docx_filename = "creative_report.docx"
    creative_docx_file = markdown_to_docx(creative_response.text, creative_docx_filename)
  
    return creative_docx_file



# Define structured output using Pydantic
class FactCheckURLs(BaseModel):
    claim: str = Field(description="The claim being fact-checked.")
    urls: list[HttpUrl] = Field(description="A list of URLs that contain relevant news articles.")

# Initialize output parser
parser = PydanticOutputParser(pydantic_object=FactCheckURLs)


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
            query = f"Find credible news sources and/or academic papers related to this claim: {user_claim}.{parser.get_format_instructions()}"
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

            {news_texts[:3000]}  # Limit to avoid token overflow

            Analyze the claim using these sources:
            - Identify which parts are **true, false, or uncertain**.
            - Highlight contradictions between sources.
            - Reference sources when making a judgment.
            """
            fact_check_report = llm_gemini.generate_content(fact_check_prompt)
            fact_check_report= fact_check_report.text
           
            # Step 5: Generate report
            formatted_report = generate_report(fact_check_report, urls_to_check)
            
            # Display report
            st.subheader("Fact-Check Report")
            st.write(formatted_report)

            st.subheader("Download Report")

            # PDF Download Button
            docx_filename = "fact_check_report.docx" # You must specify
            docx_file = markdown_to_docx(formatted_report, docx_filename)

            pdf_filename = "fact_check_report.pdf"
            pdf_file = convert_docx_to_pdf(docx_file, pdf_filename) # pdf_file will have the filename as before.
            creative_file= generate_creative_writing_from_report(formatted_report, fact_check_data.urls)

            if pdf_file:
                try:
                    with open(pdf_file, "rb") as file: # Open the actual pdf file
                        pdf_bytes = file.read()
                    st.download_button(
                        label="📄 Download Report as PDF",
                        data=pdf_bytes, # This must be the pdf bytes, not the docx
                        file_name=pdf_filename,
                        mime="application/pdf"
                    )
                except Exception as e:
                    st.error(f"Error reading PDF file: {e}")
            else:
                st.error("Failed to convert DOCX to PDF.")

            if creative_file:
                try:
                    with open(creative_file, "rb") as file:
                        file_bytes = file.read()
                    st.download_button(
                        label="📄 Download as Op-Ed",
                        data=file_bytes,
                        file_name="creative_writing.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )
                except Exception as e:
                    st.error(f"Error reading op-ed file: {e}")
            else:
                st.error("Failed to create op-ed file")
    
            google_doc_url = upload_docx_to_drive(docx_file, drive_folder_link)

            if google_doc_url:
             # Button to open the Google Doc
             st.write("Access as google doc:", google_doc_url)
            
            
 
        except Exception as e:
            st.error(f"An error occurred: {e}")
            st.write("Raw response from the agent:", formatted_report)





