from typing import List, Union
from pydantic import BaseModel

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
    listingId: str
    gradYear: str
    gradMonth: str
    firstName: str
    lastName: str
    preferredName: str
    major: str
    minor: str
    gpa: str
    hasGpa: bool
    email: str
    phone: str
    linkedin: str
    website: str
    resume: str
    image: str
    colleges: College
    events: Union[None, dict]
    responses: List[Response]