FROM python:3.10 as requirements-stage
WORKDIR /tmp
RUN pip install poetry
COPY ./pyproject.toml ./poetry.lock* /tmp/
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

FROM python:3.10
WORKDIR /autodp
COPY --from=requirements-stage /tmp/requirements.txt /autodp/requirements.txt
COPY .env /autodp/.env
RUN pip install --no-cache-dir --upgrade -r /autodp/requirements.txt
COPY ./src /autodp/src
COPY ./alembic.ini /autodp/alembic.ini
COPY ./alembic /autodp/alembic
CMD ["uvicorn", "src:init_app", "--host", "0.0.0.0", "--port", "80"]
