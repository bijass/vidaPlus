from sqlalchemy import select

from vidaplus.main.schemas.admission import AdmissionSchema, CreateAdmissionSchema, UpdateAdmissionSchema
from vidaplus.models.config.connection import DatabaseConnectionHandler
from vidaplus.models.entities.admission import Admission
from vidaplus.models.repositories.interfaces.admission_repository_interface import AdmissionRepositoryInterface


class AdmissionRepository(AdmissionRepositoryInterface):
    def create(self, data: CreateAdmissionSchema) -> AdmissionSchema:
        with DatabaseConnectionHandler() as db:
            try:
                admission = Admission(**data.model_dump())
                db.session.add(admission)
                db.session.commit()
                db.session.refresh(admission)
                return AdmissionSchema.model_validate(admission)
            except Exception as e:
                db.session.rollback()
                raise e

    def all(self) -> list[AdmissionSchema]:
        with DatabaseConnectionHandler() as db:
            try:
                admissions = db.session.query(Admission).all()
                return [AdmissionSchema.model_validate(admission) for admission in admissions]
            except Exception as e:
                db.session.rollback()
                raise e

    def get_by_id(self, admission_id: int) -> AdmissionSchema | None:
        with DatabaseConnectionHandler() as db:
            try:
                admission = db.session.scalar(select(Admission).where(Admission.id == admission_id))
                return AdmissionSchema.model_validate(admission) if admission else None
            except Exception as e:
                db.session.rollback()
                raise e

    def update(self, admission_id: int, data: UpdateAdmissionSchema) -> AdmissionSchema:
        with DatabaseConnectionHandler() as db:
            try:
                admission = db.session.scalar(select(Admission).where(Admission.id == admission_id))

                for key, value in data.model_dump().items():
                    if value is not None:
                        setattr(admission, key, value)

                db.session.commit()
                db.session.refresh(admission)
                return AdmissionSchema.model_validate(admission)
            except Exception as e:
                db.session.rollback()
                raise e

    def delete(self, admission_id: int) -> None:
        with DatabaseConnectionHandler() as db:
            try:
                admission = db.session.scalar(select(Admission).where(Admission.id == admission_id))
                db.session.delete(admission)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                raise e
