FROM python:3.12.10-alpine

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY uv.lock pyproject.toml alembic.ini ./

RUN uv venv
RUN source .venv/bin/activate
RUN uv sync --no-dev

COPY vidaplus vidaplus
COPY migrations migrations

CMD ["sh", "-c", ".venv/bin/python -m alembic upgrade head && .venv/bin/python -m fastapi run vidaplus/run.py --host 0.0.0.0"]
