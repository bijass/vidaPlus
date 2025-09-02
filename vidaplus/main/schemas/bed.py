from pydantic import BaseModel, ConfigDict

from vidaplus.main.enums.bed_status import BedStatus
from vidaplus.main.enums.bed_types import BedTypes
from vidaplus.main.schemas.unit import UnitSchema


class CreateBedSchema(BaseModel):
    unit_id: int
    type: BedTypes
    status: BedStatus

    model_config = ConfigDict(from_attributes=True)


class BedSchema(CreateBedSchema):
    id: int
    unit: UnitSchema
