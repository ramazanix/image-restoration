from pydantic import BaseModel


class ImageBase(BaseModel):
    name: str
    size: int
    location: str

    class Config:
        orm_mode = True


class ImageSchema(BaseModel):
    id: str
    name: str
    size: int
    location: str
    user_id: str
