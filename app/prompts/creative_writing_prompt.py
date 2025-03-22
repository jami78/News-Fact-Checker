def get_creative_writing_prompt(formatted_report: str, urls_to_check: list) -> str:
    """Generates the creative writing (Op-Ed) prompt for the LLM"""
    formatted_sources = "\n".join(f"- {url}" for url in urls_to_check)

    return f"""
    Based on the above fact-checking report, write an op-ed that conveys the contents in a human-friendly way. 
    The op-ed should feel informative and engaging, incorporating themes from the fact-check.
    Make it at least 600 words.

    At the end, include a **'Sources'** section listing the URLs of the references used for fact-checking.

    ---
    **Sources:**
    {formatted_sources}
    """
