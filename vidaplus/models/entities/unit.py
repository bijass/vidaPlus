from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from vidaplus.models.config.base import Base

if TYPE_CHECKING:
    from vidaplus.models.entities.bed import Bed
    from vidaplus.models.entities.supply import Supply


class Unit(Base):
    __tablename__ = 'unit'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    address: Mapped[str] = mapped_column(String, nullable=False)

    beds: Mapped[list['Bed']] = relationship(
        'Bed',
        back_populates='unit',
        cascade='all, delete-orphan',
        lazy='selectin',
    )
    supplies: Mapped[list['Supply']] = relationship(
        'Supply',
        back_populates='unit',
        cascade='all, delete-orphan',
        lazy='selectin',
    )
