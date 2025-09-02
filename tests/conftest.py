import random
from datetime import datetime, timedelta
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, StaticPool, create_engine

from vidaplus.main.enums.appointment_status import AppointmentStatus
from vidaplus.main.enums.appointment_types import AppointmentTypes
from vidaplus.main.enums.roles import Roles
from vidaplus.main.schemas.appointment import AppointmentSchema
from vidaplus.main.schemas.auth import ResponseAuthToken
from vidaplus.main.schemas.bed import BedSchema
from vidaplus.main.schemas.unit import UnitSchema
from vidaplus.main.schemas.user import UserSchema
from vidaplus.models.config.base import Base
from vidaplus.models.config.connection import DatabaseConnectionHandler
from vidaplus.models.entities.appointment import Appointment
from vidaplus.models.entities.bed import Bed
from vidaplus.models.entities.unit import Unit
from vidaplus.models.entities.user import User
from vidaplus.run import app
from vidaplus.settings import Settings


@pytest.fixture
def engine(monkeypatch: pytest.MonkeyPatch) -> Generator[Engine, None, None]:
    monkeypatch.setenv('DATABASE_URL', 'sqlite:///:memory:')

    engine = create_engine(Settings().DATABASE_URL, connect_args={'check_same_thread': False}, poolclass=StaticPool)

    monkeypatch.setattr(DatabaseConnectionHandler, '_DatabaseConnectionHandler__create_engine', lambda x: engine)

    Base.metadata.create_all(engine)

    yield engine

    Base.metadata.drop_all(engine)


@pytest.fixture
def client(engine: Engine) -> Generator[TestClient, None, None]:
    with TestClient(app) as client:
        yield client


@pytest.fixture
def patient(engine: Engine) -> UserSchema:
    user = User(
        name='John Doe',
        email='johndoe@example.com',
        password='ilovepotatos',
        role=Roles.PATIENT,
    )

    with DatabaseConnectionHandler() as db:
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)

    return UserSchema.model_validate(user)


@pytest.fixture
def another_patient(engine: Engine) -> UserSchema:
    user = User(
        name='Jane Doe',
        email='janedoe@example.com',
        password='ilovepotatos',
        role=Roles.PATIENT,
    )

    with DatabaseConnectionHandler() as db:
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)

    return UserSchema.model_validate(user)


@pytest.fixture
def admin(engine: Engine) -> UserSchema:
    user = User(
        name='Admin',
        email='admin@example.com',
        password='ilovepotatos',
        role=Roles.ADMIN,
    )

    with DatabaseConnectionHandler() as db:
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)

    return UserSchema.model_validate(user)


@pytest.fixture
def token(client: TestClient, patient: UserSchema) -> str:
    data = {
        'email': 'johndoe@example.com',
        'password': 'ilovepotatos',
    }

    response = client.post('/api/auth/token', json=data)
    return ResponseAuthToken(**response.json()).access_token


@pytest.fixture
def admin_token(client: TestClient, admin: UserSchema) -> str:
    data = {
        'email': 'admin@example.com',
        'password': 'ilovepotatos',
    }

    response = client.post('/api/auth/token', json=data)
    return ResponseAuthToken(**response.json()).access_token


@pytest.fixture
def healthcare_professional(engine: Engine) -> UserSchema:
    user = User(
        name='Healthcare Professional',
        email='healthcareprofessional@example.com',
        password='iloveapples',
        role=Roles.HEALTHCARE_PROFESSIONAL,
    )

    with DatabaseConnectionHandler() as db:
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)

        return UserSchema.model_validate(user)


@pytest.fixture
def another_healthcare_professional(engine: Engine) -> UserSchema:
    user = User(
        name='Another Healthcare Professional',
        email='anotherhealthcareprofessional@example.com',
        password='iloveapples',
        role=Roles.HEALTHCARE_PROFESSIONAL,
    )

    with DatabaseConnectionHandler() as db:
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)

    return UserSchema.model_validate(user)


@pytest.fixture
def healthcare_professional_token(client: TestClient, healthcare_professional: UserSchema) -> str:
    data = {
        'email': 'healthcareprofessional@example.com',
        'password': 'iloveapples',
    }

    response = client.post('/api/auth/token', json=data)
    return ResponseAuthToken(**response.json()).access_token


@pytest.fixture
def appointment(engine: Engine, patient: UserSchema, healthcare_professional: UserSchema) -> AppointmentSchema:
    appointment = Appointment(
        patient_id=patient.id,
        professional_id=healthcare_professional.id,
        type=AppointmentTypes.CONSULTATION,
        status=AppointmentStatus.SCHEDULED,
        notes='Agendamento genérico',
        date_time=datetime.now() + timedelta(minutes=30),
        estimated_duration=30,
        location='Sala 1',
    )

    with DatabaseConnectionHandler() as db:
        db.session.add(appointment)
        db.session.commit()
        db.session.refresh(appointment)

    return AppointmentSchema.model_validate(appointment)


@pytest.fixture
def date_in_future() -> str:
    future_date = datetime.now() + timedelta(days=random.randint(1, 30))
    return future_date.isoformat()


@pytest.fixture
def unit_payload() -> dict:
    return {'name': 'Unidade Central', 'address': 'Av. Principal, 123'}


@pytest.fixture
def unit(engine: Engine) -> UnitSchema:
    u = Unit(name='Unidade Fixture', address='Rua Fixture, 1')
    with DatabaseConnectionHandler() as db:
        db.session.add(u)
        db.session.commit()
        db.session.refresh(u)
    return UnitSchema.model_validate(u)


@pytest.fixture
def bed(engine: Engine, unit: UnitSchema) -> BedSchema:
    b = Bed(unit_id=unit.id, type='STANDARD', status='AVAILABLE')
    with DatabaseConnectionHandler() as db:
        db.session.add(b)
        db.session.commit()
        db.session.refresh(b)
    return BedSchema.model_validate(b)
