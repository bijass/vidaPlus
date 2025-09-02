from sqlalchemy import select

from vidaplus.main.schemas.unit import CreateUnitSchema, UnitSchema
from vidaplus.models.config.connection import DatabaseConnectionHandler
from vidaplus.models.entities.unit import Unit
from vidaplus.models.repositories.interfaces.unit_repository_interface import UnitRepositoryInterface


class UnitRepository(UnitRepositoryInterface):
    def create(self, unit: CreateUnitSchema) -> UnitSchema:
        with DatabaseConnectionHandler() as db:
            try:
                unit_db = Unit(**unit.model_dump())
                db.session.add(unit_db)
                db.session.commit()
                db.session.refresh(unit_db)

                return UnitSchema.model_validate(unit_db)
            except Exception as ex:
                db.session.rollback()
                raise ex

    def all(self) -> list[UnitSchema]:
        with DatabaseConnectionHandler() as db:
            try:
                units = db.session.scalars(select(Unit))
                return [UnitSchema.model_validate(unit) for unit in units]
            except Exception as ex:
                db.session.rollback()
                raise ex

    def get_by_id(self, unit_id: int) -> UnitSchema | None:
        with DatabaseConnectionHandler() as db:
            try:
                unit = db.session.scalar(select(Unit).where(Unit.id == unit_id))

                if not unit:
                    return None

                return UnitSchema.model_validate(unit)
            except Exception as ex:
                db.session.rollback()
                raise ex

    def update(self, unit_id: int, unit: CreateUnitSchema) -> UnitSchema:
        with DatabaseConnectionHandler() as db:
            try:
                unit_db = db.session.scalar(select(Unit).where(Unit.id == unit_id))

                for k, v in unit.model_dump().items():
                    setattr(unit_db, k, v)

                db.session.commit()
                db.session.refresh(unit_db)

                return UnitSchema.model_validate(unit_db)
            except Exception as ex:
                db.session.rollback()
                raise ex

    def delete(self, unit_id: int) -> None:
        with DatabaseConnectionHandler() as db:
            try:
                unit = db.session.get(Unit, unit_id)
                db.session.delete(unit)
                db.session.commit()
            except Exception as ex:
                db.session.rollback()
                raise ex
