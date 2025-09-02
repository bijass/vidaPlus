from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class CreateAdmissionSchema(BaseModel):
    patient_id: UUID
    bed_id: int

    model_config = ConfigDict(from_attributes=True)


class AdmissionSchema(CreateAdmissionSchema):
    id: int
    admitted_at: datetime
    discharged_at: datetime | None


class UpdateAdmissionSchema(BaseModel):
    patient_id: UUID | None = None
    bed_id: int | None = None
    admitted_at: datetime | None = None
    discharged_at: datetime | None = None
