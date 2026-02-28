from fastapi import FastAPI
from scalar_fastapi import get_scalar_api_reference

from app.modules.research.schema import ResearchInput
from app.modules.research.tasks import report_research_task

app = FastAPI()


@app.post("/ask")
def do_research(body: ResearchInput):

    report_research_task.delay(body.idea)  # type: ignore

    return {"message": "Researching..."}


@app.get("/scalar")
def get_scalar():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title=app.title,
    )
