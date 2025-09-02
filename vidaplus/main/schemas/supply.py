from pydantic import BaseModel, ConfigDict


class CreateSupplySchema(BaseModel):
    unit_id: int
    name: str
    quantity: int
    min_level: int

    model_config = ConfigDict(from_attributes=True)


class SupplySchema(CreateSupplySchema):
    id: int
