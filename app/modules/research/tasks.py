from markdown import markdown
from weasyprint import HTML

from app.modules.research.methods import generate_queries, search_web, generate_report
from app.celery_app import celery_app


def report_research(idea: str):
    research_context = ""
    queries = generate_queries(idea)

    for query in queries.queries:
        result = search_web(query)
        research_context += f"Query: {query} \n\n Result: {result} \n\n\n"

    research_report = generate_report(idea, research_context)
    if not research_report:
        raise ValueError("No research report generated")

    result_html = markdown(research_report, output_format="html")
    result_pdf = HTML(string=result_html).write_pdf(f"{idea}.pdf")
    return result_pdf


@celery_app.task
def report_research_task(idea: str):
    return report_research(idea)
