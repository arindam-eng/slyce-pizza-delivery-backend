from pydantic import BaseModel, Field, EmailStr, validator

class CategoryOut(BaseModel):
    id: int
    name: str
    class Config:
        from_attributes = True