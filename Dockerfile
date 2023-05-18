FROM python:3.10 as requirements-stage
WORKDIR /tmp
RUN pip install poetry
COPY ./pyproject.toml ./poetry.lock* /tmp/
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

FROM python:3.10
WORKDIR /photo-restoration
COPY --from=requirements-stage /tmp/requirements.txt /photo-restoration/requirements.txt
COPY .env /photo-restoration/.env
RUN pip install --no-cache-dir --upgrade -r /photo-restoration/requirements.txt
COPY ./src /photo-restoration/src
COPY ./alembic.ini /photo-restoration/alembic.ini
COPY ./alembic /photo-restoration/alembic
CMD ["uvicorn", "src:init_app", "--host", "0.0.0.0", "--port", "80"]
