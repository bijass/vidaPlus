from pydantic import BaseModel, ConfigDict


class CreateUnitSchema(BaseModel):
    name: str
    address: str

    model_config = ConfigDict(from_attributes=True)


class UnitSchema(CreateUnitSchema):
    id: int
