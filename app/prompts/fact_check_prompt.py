def get_fact_check_prompt(claim: str, news_texts: str) -> str:
    """Generates the fact-checking prompt for the LLM"""
    return f"""
    Claim: "{claim}"

    Below are news articles related to the claim:

    {news_texts[:3000]}

    Analyze the claim using these sources. Do the following:
    - Explain the claim in your own words.
    - Identify which parts of the claim are **true, false, or uncertain**.
    - Highlight contradictions between sources.
    - Reference sources when making a judgment.
    - Create a detailed report outlining all the information.
    - Provide your degree of certainty on that claim in percentage.
    - If the sources do not indicate anything, write based on what you know.
    """
