from typing import Union, List
from pydantic import BaseModel


class Question(BaseModel):
    question: str
    additional: str


class Listing(BaseModel):
    listingId: str
    dateCreated: str
    deadline: str
    isVisible: Union[bool, None]
    questions: List[Question]
    title: str

    @classmethod
    def from_dynamodb_item(cls, item: dict):
        """Create a Listing instance from a DynamoDB item."""
        return cls(
            listingId=item.get("listingId"),
            dateCreated=item.get("dateCreated"),
            deadline=item.get("deadline"),
            isVisible=item.get("isVisible"),
            questions=[Question(**q) for q in item.get("questions", [])],
            title=item.get("title"),
        )
