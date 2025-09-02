from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import UUID, DateTime, Enum, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from vidaplus.main.enums.roles import Roles
from vidaplus.models.config.base import Base

if TYPE_CHECKING:
    from vidaplus.models.entities.admission import Admission
    from vidaplus.models.entities.appointment import Appointment


class User(Base):
    __tablename__ = 'user'

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[Roles] = mapped_column(Enum(Roles), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    patient_appointments: Mapped[list['Appointment']] = relationship(
        'Appointment', back_populates='patient', foreign_keys='[Appointment.patient_id]', cascade='all, delete-orphan'
    )
    patient_admissions: Mapped['Admission'] = relationship(
        'Admission', back_populates='patient', foreign_keys='[Admission.patient_id]', cascade='all, delete-orphan'
    )

    professional_appointments: Mapped[list['Appointment']] = relationship(
        'Appointment',
        back_populates='professional',
        foreign_keys='[Appointment.professional_id]',
        cascade='all, delete-orphan',
    )
