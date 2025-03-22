from datetime import datetime
# Define report generator
def generate_report( fact_check_result, urls):
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report = f"""
    
    # Fact-Check Report
    Date: {current_date}

    ## Fact-Check Findings:
    {fact_check_result}

    ## Sources:
    """ + "\n".join(f"- {url}" for url in urls)

    return report