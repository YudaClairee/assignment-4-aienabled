from pydantic import BaseModel


class APITestCase(BaseModel):
    scenario: str
    method: str
    path: str
    payload: dict[str, str | int | float | None] = {}


class TestCasesSchema(BaseModel):
    cases: list[APITestCase]


class TestCasesInput(BaseModel):
    api_description: str
    base_url: str
