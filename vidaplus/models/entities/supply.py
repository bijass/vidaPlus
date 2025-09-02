from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from vidaplus.models.config.base import Base

if TYPE_CHECKING:
    from vidaplus.models.entities.unit import Unit


class Supply(Base):
    __tablename__ = 'supply'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    min_level: Mapped[int] = mapped_column(Integer, nullable=False)

    unit_id: Mapped[int] = mapped_column(Integer, ForeignKey('unit.id'), nullable=False)
    unit: Mapped['Unit'] = relationship('Unit', back_populates='supplies')
