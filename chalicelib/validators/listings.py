from pydantic import BaseModel, validator
from chalicelib.models.listing import Listing


class UpdateFieldRequest(BaseModel):
    field: str
    value: str

    @validator("field")
    def validate_field(cls, v):
        valid_fields = cls.get_valid_fields()
        if v not in valid_fields:
            raise ValueError(f"Invalid field: {v}. Allowed fields: {valid_fields}")
        return v

    @classmethod
    def get_valid_fields(cls):
        return [field for field in Listing.__annotations__.keys()]
