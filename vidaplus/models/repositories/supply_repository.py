from sqlalchemy import select

from vidaplus.main.schemas.supply import CreateSupplySchema, SupplySchema
from vidaplus.models.config.connection import DatabaseConnectionHandler
from vidaplus.models.entities.supply import Supply
from vidaplus.models.repositories.interfaces.supply_repository_interface import SupplyRepositoryInterface


class SupplyRepository(SupplyRepositoryInterface):
    def create(self, data: CreateSupplySchema) -> SupplySchema:
        with DatabaseConnectionHandler() as db:
            try:
                supply = Supply(**data.model_dump())
                db.session.add(supply)
                db.session.commit()
                db.session.refresh(supply)
                return SupplySchema.model_validate(supply)
            except Exception as ex:
                db.session.rollback()
                raise ex

    def all(self) -> list[SupplySchema]:
        with DatabaseConnectionHandler() as db:
            try:
                supplies = db.session.query(Supply).all()
                return [SupplySchema.model_validate(supply) for supply in supplies]
            except Exception as ex:
                db.session.rollback()
                raise ex

    def get_by_id(self, supply_id: int) -> SupplySchema | None:
        with DatabaseConnectionHandler() as db:
            try:
                supply = db.session.scalar(select(Supply).where(Supply.id == supply_id))
                return SupplySchema.model_validate(supply) if supply else None
            except Exception as ex:
                db.session.rollback()
                raise ex

    def update(self, supply_id: int, data: CreateSupplySchema) -> SupplySchema:
        with DatabaseConnectionHandler() as db:
            try:
                supply = db.session.scalar(select(Supply).where(Supply.id == supply_id))

                for key, value in data.model_dump().items():
                    setattr(supply, key, value)

                db.session.commit()
                db.session.refresh(supply)

                return SupplySchema.model_validate(supply)
            except Exception as ex:
                db.session.rollback()
                raise ex

    def delete(self, supply_id: int) -> None:
        with DatabaseConnectionHandler() as db:
            try:
                supply = db.session.scalar(select(Supply).where(Supply.id == supply_id))
                db.session.delete(supply)
                db.session.commit()
            except Exception as ex:
                db.session.rollback()
                raise ex
