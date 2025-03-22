from langchain.output_parsers import PydanticOutputParser
from app.schemas.factcheckurl import FactCheckURLs
from fastapi import HTTPException

#  Initialize the parser
parser = PydanticOutputParser(pydantic_object=FactCheckURLs)

def parse_fact_check_response(fact_check_data: str) -> FactCheckURLs:
    """Parses the AI response to ensure proper formatting."""

    if isinstance(fact_check_data, str):
        fact_check_data = fact_check_data.strip('*`')

    try:
        fact_check_data = parser.parse(fact_check_data)
        if not isinstance(fact_check_data, str):  
            fact_check_data = fact_check_data.model_dump_json()  
        return parser.parse(fact_check_data)

    except Exception as e:
        print(f"Error parsing response: {e}")
        print(f"Raw response: {fact_check_data}")
        print(f"Expected format: {parser.get_format_instructions()}")
        raise HTTPException(status_code=500, detail="Error parsing URLs response.")
