from sqlalchemy import select

from vidaplus.main.schemas.bed import BedSchema, CreateBedSchema
from vidaplus.models.config.connection import DatabaseConnectionHandler
from vidaplus.models.entities.bed import Bed
from vidaplus.models.repositories.interfaces.bed_repository_interface import BedRepositoryInterface


class BedRepository(BedRepositoryInterface):
    def create(self, bed: CreateBedSchema) -> BedSchema:
        with DatabaseConnectionHandler() as db:
            try:
                bed_db = Bed(**bed.model_dump())
                db.session.add(bed_db)
                db.session.commit()
                db.session.refresh(bed_db)
                return BedSchema.model_validate(bed_db)
            except Exception as e:
                db.session.rollback()
                raise e

    def all(self) -> list[BedSchema]:
        with DatabaseConnectionHandler() as db:
            try:
                beds = db.session.query(Bed).all()
                return [BedSchema.model_validate(bed) for bed in beds]
            except Exception as e:
                db.session.rollback()
                raise e

    def get_by_id(self, bed_id: int) -> BedSchema | None:
        with DatabaseConnectionHandler() as db:
            try:
                bed = db.session.scalar(select(Bed).where(Bed.id == bed_id))

                return BedSchema.model_validate(bed) if bed else None
            except Exception as e:
                db.session.rollback()
                raise e

    def update(self, bed_id: int, bed: CreateBedSchema) -> BedSchema:
        with DatabaseConnectionHandler() as db:
            try:
                bed_db = db.session.scalar(select(Bed).where(Bed.id == bed_id))

                for k, v in bed.model_dump().items():
                    setattr(bed_db, k, v)

                db.session.commit()
                db.session.refresh(bed_db)

                return BedSchema.model_validate(bed_db)
            except Exception as e:
                db.session.rollback()
                raise e

    def delete(self, bed_id: int) -> None:
        with DatabaseConnectionHandler() as db:
            try:
                bed = db.session.scalar(select(Bed).where(Bed.id == bed_id))

                db.session.delete(bed)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                raise e
