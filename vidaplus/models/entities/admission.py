from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import UUID, DateTime, ForeignKey, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from vidaplus.models.config.base import Base

if TYPE_CHECKING:
    from vidaplus.models.entities.bed import Bed
    from vidaplus.models.entities.user import User


class Admission(Base):
    __tablename__ = 'admission'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    admitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    discharged_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    bed_id: Mapped[int] = mapped_column(Integer, ForeignKey('bed.id', ondelete='CASCADE'), nullable=False)
    bed: Mapped['Bed'] = relationship('Bed', back_populates='admissions', lazy='joined')

    patient_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey('user.id', ondelete='CASCADE'), nullable=False
    )
    patient: Mapped['User'] = relationship('User', back_populates='patient_admissions', lazy='joined')
