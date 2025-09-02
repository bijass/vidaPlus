from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from vidaplus.main.enums.appointment_status import AppointmentStatus
from vidaplus.main.enums.appointment_types import AppointmentTypes
from vidaplus.models.config.base import Base

if TYPE_CHECKING:
    from vidaplus.models.entities.user import User


class Appointment(Base):
    __tablename__ = 'appointment'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    date_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    type: Mapped[str] = mapped_column(Enum(AppointmentTypes), nullable=False)
    status: Mapped[str] = mapped_column(Enum(AppointmentStatus), nullable=False)
    estimated_duration: Mapped[int] = mapped_column(Integer, nullable=False)
    location: Mapped[str] = mapped_column(String, nullable=False)
    notes: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    patient_id: Mapped[UUID] = mapped_column(ForeignKey('user.id'))
    professional_id: Mapped[UUID] = mapped_column(ForeignKey('user.id'))

    patient: Mapped['User'] = relationship('User', foreign_keys=[patient_id], back_populates='patient_appointments')
    professional: Mapped['User'] = relationship(
        'User', foreign_keys=[professional_id], back_populates='professional_appointments'
    )
