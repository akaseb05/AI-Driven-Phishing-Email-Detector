from fastapi import FastAPI
from pydantic import BaseModel, EmailStr
from typing import List, Optional

from detector.scoring import score_email


app = FastAPI(
    title="Phishing Email Detector (Prototype)",
    description="Very early version of a phishing email checker. Uses simple rules for now, AI coming later.",
    version="0.0.1",
)


class EmailInput(BaseModel):
    subject: str
    body: str
    from_address: EmailStr
    to_addresses: List[EmailStr]
    cc_addresses: Optional[List[EmailStr]] = []


@app.get("/")
def home():
    return {
        "message": "Phishing detector API is up.",
        "hint": "Go to /docs to try the classify-email endpoint.",
        "status": "prototype",
    }


@app.post("/classify-email")
def classify_email(email: EmailInput):
    """
    Take basic email info and return:
    - phishing_probability (0–1)
    - small breakdown of scores
    - simple explanation in plain English

    TODO:
    - add batch endpoint
    - plug in real AI / ML instead of just rules
    """
    result = score_email(email.dict())
    return result
