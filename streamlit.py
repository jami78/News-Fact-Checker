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

# Load environment variables
load_dotenv(dotenv_path='/teamspace/studios/this_studio/env.txt')

# Initialize LLMs
llm_groq = ChatGroq(model='llama3-70b-8192')
llm_openai = ChatOpenAI(model_name="gpt-4", temperature=0)

# Search functions for Google, DuckDuckGo, Tavily
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
    """
    Generates a fact-check report with proper formatting and line wrapping.
    """
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
{textwrap.fill(fact_check_result.content)}
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

# Streamlit interface
st.title("📰 Fact-Checking Tool")
st.write("Enter a claim to fact-check and get a detailed report.")

# User input for the claim
user_claim = st.text_input("Enter the claim to fact-check:",)

if st.button("Fact-Check"):
    with st.spinner("Analyzing the claim..."):
        try:
            # Step 1: Find relevant sources
            query = f"Find credible news sources (text only) related to this claim: {user_claim}.{parser.get_format_instructions()}"
            fact_check_data = agent.run(query)

            # Step 2: Parse the response
            fact_check_data = parser.parse(fact_check_data)

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
            fact_check_report = llm_openai.invoke(fact_check_prompt)

            # Step 5: Generate the report
            formatted_report = generate_report(fact_check_report, fact_check_data.urls)

            # Display the report
            st.subheader("Fact-Check Report")
            st.write(formatted_report)

            # Step 6: Save the report as a PDF
            pdf_filename = save_report_as_pdf(formatted_report)
            with open(pdf_filename, "rb") as pdf_file:
                st.download_button(
                    label="Download Report as PDF",
                    data=pdf_file,
                    file_name=pdf_filename,
                    mime="application/pdf"
                )

            st.success("✅ Fact-checking completed! Report generated and available for download.")
        except Exception as e:
            st.error(f"An error occurred: {e}")
            st.write("Raw response from the agent:", formatted_report)