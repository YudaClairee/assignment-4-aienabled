import json
import logging
import requests

from app.utils.openai import client
from .prompt import QA_REPORT_SYSTEM_PROMPT
from .schema import APITestCase, TestCasesSchema

logger = logging.getLogger(__name__)


def generate_test_cases(api_description: str, base_url: str) -> TestCasesSchema:
    response = client.chat.completions.parse(
        model="google/gemini-3-flash-preview",
        messages=[
            {
                "role": "system",
                "content": """
                    You are an Automated QA Agent. The user will provide a description of an API and its base URL. 
                    Your task is to generate EXACTLY 8 distinct test scenarios covering these categories:
                    1. Happy Path (1 case) - valid, complete payload
                    2. Input Validation (2 cases) - missing required fields, wrong data types
                    3. Boundary Testing (2 cases) - empty strings, extremely large numbers, negative values
                    4. Security (2 cases) - SQL injection attempt in string fields, XSS payload in string fields
                    5. Null/Empty Payload (1 case) - completely empty or null body
                    Return the HTTP method, endpoint path (relative), and JSON payload needed.
                """,
            },
            {
                "role": "user",
                "content": f"API Description: {api_description}\nBase URL: {base_url}",
            },
        ],
        response_format=TestCasesSchema,
    )

    if not response:
        raise ValueError("No response from the model")

    parsed_response = response.choices[0].message.parsed.model_dump()  # type: ignore
    logger.info(f"Parsed response: {parsed_response}")
    return TestCasesSchema(**parsed_response)


def execute_test_cases(base_url: str, test_case: APITestCase) -> str:
    full_url = f"{base_url.rstrip('/')}/{test_case.path.lstrip('/')}"
    method = test_case.method.upper()

    logger.info(f"Executing {method} {full_url} for scenario: {test_case.scenario}")

    try:
        if method == "POST":
            res = requests.post(full_url, json=test_case.payload)
        elif method == "PUT":
            res = requests.put(full_url, json=test_case.payload)
        elif method == "PATCH":
            res = requests.patch(full_url, json=test_case.payload)
        elif method == "DELETE":
            res = requests.delete(full_url, json=test_case.payload)
        else:
            res = requests.get(full_url, params=test_case.payload)

        execution_result = {
            "scenario": test_case.scenario,
            "target": full_url,
            "status_code": res.status_code,
            "response_body": res.text,
        }
    except Exception as e:
        execution_result = {
            "scenario": test_case.scenario,
            "target": full_url,
            "error": str(e),
        }

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "system",
                "content": """
                You are a QA Log Evaluator. You will receive an API test execution result that includes the scenario type, target URL, HTTP status code, and response body.

                Evaluate whether the API behavior is CORRECT based on the scenario:
                - "Happy Path" => expect 2xx status. If not, it's a FAIL.
                - "Input Validation" or "Boundary Testing" => expect 4xx (e.g. 400, 422). If it returns 2xx or 5xx, it's a FAIL.
                - "Security" => expect 4xx. If it returns 2xx or 5xx, it's a FAIL.
                - "Null/Empty Payload" => expect 4xx. If it crashes with 5xx, it's a FAIL.

                Output format:
                - Verdict: PASS or FAIL
                - Reason: brief explanation
                """,
            },
            {
                "role": "user",
                "content": f"Execution Result: {json.dumps(execution_result)}",
            },
        ],
        extra_body={"reasoning": {"enabled": True}},
    )

    if not response:
        raise ValueError("No response from the model")

    return response.choices[0].message.content  # type: ignore


def generate_qa_report(base_url: str, api_description: str, execution_logs: list[str]):
    formatted_logs = "\n\n---\n\n".join(
        f"Test {i + 1}:\n{log}" for i, log in enumerate(execution_logs)
    )

    print(f"Formatted logs: {formatted_logs}")

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "system",
                "content": QA_REPORT_SYSTEM_PROMPT.format(
                    base_url=base_url, api_description=api_description
                ),
            },
            {
                "role": "user",
                "content": f"Here are the execution logs from all test scenarios:\n\n{formatted_logs}\n\nGenerate the final QA report based on these results.",
            },
        ],
        extra_body={"reasoning": {"enabled": True}},
    )

    return response.choices[0].message.content
