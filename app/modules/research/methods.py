import json
import logging

from app.modules.research.prompt import REPORT_SYSTEM_PROMPT
from app.modules.research.schema import QueriesSchema
from app.utils.openai import client
from app.utils.tavily import tavily_client


logger = logging.getLogger(__name__)


def generate_queries(idea: str) -> QueriesSchema:
    response = client.chat.completions.parse(
        model="google/gemini-3-flash-preview",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a highly analytical Market Research and Competitive Intelligence Agent. "
                    "The user will provide a SaaS product idea or niche. "
                    "Your task is to generate EXACTLY 5 highly targeted Google search queries to analyze the market. "
                    "The queries MUST cover these 4 angles: "
                    "1. Finding direct existing competitors (e.g., 'SaaS for [idea] alternatives'). "
                    "2. Investigating their pricing models (e.g., '[idea] software pricing tiers'). "
                    "3. Discovering core features of top players. "
                    "4. Finding user complaints or raw reviews on forums (e.g., 'site:reddit.com [idea] software complaints' or 'why [idea] software sucks'). "
                    "Return only the queries."
                ),
            },
            {"role": "user", "content": f"SaaS Product Idea: {idea}"},
        ],
        response_format=QueriesSchema,
    )

    if not response:
        raise ValueError("No response from the model")

    parsed_response = response.choices[0].message.parsed.model_dump()  # type: ignore
    logger.info(f"Parsed response: {parsed_response}")
    return QueriesSchema(**parsed_response)


def search_web(query: str) -> str:
    result = tavily_client.search(
        query=query, search_depth="advanced", include_raw_content="markdown"
    )
    print(f"Search result: {result}")

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a ruthless Data Extraction Bot for SaaS Competitive Intelligence. "
                    "Your job is to scan the following search results and extract ONLY hard facts. "
                    "Focus strictly on finding: "
                    "1. Competitor Names\n"
                    "2. Exact Pricing or Pricing Tiers (e.g., '$10/mo')\n"
                    "3. Core technical features\n"
                    "4. User complaints, bugs, or negative sentiments. "
                    "Ignore all marketing fluff. Use bullet points. "
                    "CRITICAL: Always append the exact source URL for every data point extracted."
                ),
            },
            {"role": "user", "content": f"Search Results: {json.dumps(result)}"},
        ],
        extra_body={"reasoning": {"enabled": True}},
    )

    return response.choices[0].message.content  # type: ignore


def generate_report(idea: str, research_context: str):
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "system",
                "content": REPORT_SYSTEM_PROMPT.format(
                    research_context_placeholder=idea,
                    research_context=research_context,
                ),
            },
            {"role": "user", "content": f"SaaS Product Idea: {idea}"},
        ],
        extra_body={"reasoning": {"enabled": True}},
    )

    return response.choices[0].message.content
