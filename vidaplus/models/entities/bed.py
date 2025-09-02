from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from vidaplus.main.enums.bed_status import BedStatus
from vidaplus.main.enums.bed_types import BedTypes
from vidaplus.models.config.base import Base

if TYPE_CHECKING:
    from vidaplus.models.entities.admission import Admission
    from vidaplus.models.entities.unit import Unit


class Bed(Base):
    __tablename__ = 'bed'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    type: Mapped[str] = mapped_column(Enum(BedTypes), nullable=False)
    status: Mapped[str] = mapped_column(Enum(BedStatus), nullable=False)

    unit_id: Mapped[int] = mapped_column(Integer, ForeignKey('unit.id', ondelete='CASCADE'), nullable=False)
    unit: Mapped['Unit'] = relationship(
        'Unit',
        back_populates='beds',
        lazy='joined',
    )

    admissions: Mapped[list['Admission']] = relationship(
        'Admission',
        back_populates='bed',
        cascade='all, delete-orphan',
        lazy='selectin',
    )
