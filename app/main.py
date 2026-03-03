from fastapi import FastAPI
from scalar_fastapi import get_scalar_api_reference


from app.modules.api_tester.schema import TestCasesInput
from app.modules.api_tester.tasks import qa_task

app = FastAPI()


@app.post("/qa")
def do_qa(body: TestCasesInput):
    qa_task.delay(body.api_description, body.base_url)  # type: ignore
    return {"message": "Testing API..."}


@app.get("/scalar")
def get_scalar():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title=app.title,
    )
