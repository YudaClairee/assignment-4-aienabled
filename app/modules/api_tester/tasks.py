from markdown import markdown
from weasyprint import HTML

from app.celery_app import celery_app
from app.modules.api_tester.methods import (
    generate_test_cases,
    execute_test_cases,
    generate_qa_report,
)


def run_qa_process(api_description: str, base_url: str):
    qa_log_results = []
    test_cases = generate_test_cases(api_description, base_url)

    print(f"Test cases: {test_cases.cases}")
    for test in test_cases.cases:
        result = execute_test_cases(base_url, test)
        qa_log_results.append(result)
        print(f"Test {test.scenario} result: {result}")

    print(f"QA log results: {qa_log_results}")

    qa_report_result = generate_qa_report(
        base_url=base_url,
        api_description=api_description,
        execution_logs=qa_log_results,
    )
    if not qa_report_result:
        raise ValueError("No QA report generated")

    result_html = markdown(text=qa_report_result, output_format="html")

    result_pdf = HTML(string=result_html).write_pdf("qa_report.pdf")
    return result_pdf


@celery_app.task
def qa_task(api_description: str, base_url: str):
    run_qa_process(api_description, base_url)
