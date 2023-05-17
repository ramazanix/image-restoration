from pydantic import BaseModel, UUID4, Field


class RoleSchemaBase(BaseModel):
    id: UUID4
    name: str
    description: str

    class Config:
        orm_mode = True


class RoleSchemaCreate(BaseModel):
    name: str = Field(min_length=2, max_length=20)
    description: str | None = Field(min_length=2, max_length=100)


class RoleSchemaUpdate(BaseModel):
    name: str | None = Field(min_length=2, max_length=20)
    description: str | None = Field(min_length=2, max_length=100)


class RoleSchema(RoleSchemaBase):
    users: list["UserSchemaBase"]

    class Config:
        orm_mode = True


from .user import UserSchemaBase

RoleSchema.update_forward_refs()
