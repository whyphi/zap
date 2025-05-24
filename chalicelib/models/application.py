from typing import List, Optional
from pydantic import BaseModel
from uuid import UUID


class College(BaseModel):
    CAS: bool
    Pardee: bool
    QST: bool
    COM: bool
    ENG: bool
    CFA: bool
    CDS: bool
    CGS: bool
    Sargent: bool
    SHA: bool
    Wheelock: bool
    Other: bool


class Response(BaseModel):
    question: str
    response: str


class Application(BaseModel):
    id: UUID
    listing_id: UUID
    email: str
    first_name: str
    last_name: str
    preferred_name: Optional[str]
    gpa: float
    has_gpa: bool
    grad_month: str
    grad_year: int
    image: str
    website: Optional[str]
    linkedin: Optional[str]
    resume: str
    major: str
    minor: Optional[str]
    phone: str
    colleges: College
    responses: List[Response]
