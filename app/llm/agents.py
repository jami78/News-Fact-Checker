from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain.tools import Tool
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain.tools import DuckDuckGoSearchRun, TavilySearchResults, ArxivQueryRun
from app.llm.llm_services import llm_openai
from app.prompts.agent_prompt import get_agent_prompt

# 🔹 Define Search Tools
def google_search_tool(query):
    return GoogleSerperAPIWrapper().run(query)

def duckduckgo_tool(query):
    return DuckDuckGoSearchRun().run(query)

def tavily_tool(query):
    return TavilySearchResults(search_depth="advanced", include_answer=True, include_images=True).invoke(query)

def arxiv_tool(query):
    return ArxivQueryRun().run(query)

# 🔹 Register Tools
tools = [
    Tool(name="google_search", func=google_search_tool, description="Search Google for news"),
    Tool(name="duckduckgo_search", func=duckduckgo_tool, description="Search DuckDuckGo for news"),
    Tool(name="tavily_search", func=tavily_tool, description="Search Tavily for related sources"),
    Tool(name="arxiv_tool", func=arxiv_tool, description="Search academic papers from ArXiv")
]

# 🔹 Initialize the Multi-LLM Agent
custom_prompt = get_agent_prompt()

agent_init = create_tool_calling_agent(llm_openai, tools, custom_prompt)

agent= AgentExecutor(
    agent=agent_init,
    tools= tools,
    handle_parsing_errors=True,
    return_intermediate_steps=False,
    max_iterations=7,
    verbose= True

)