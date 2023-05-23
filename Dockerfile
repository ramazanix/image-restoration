FROM python:3.10 as requirements-stage
WORKDIR /tmp
RUN pip install poetry
COPY ./pyproject.toml ./poetry.lock* /tmp/
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

FROM python:3.10
WORKDIR /image-restoration
COPY --from=requirements-stage /tmp/requirements.txt /image-restoration/requirements.txt
COPY .env /image-restoration/.env
RUN pip install --no-cache-dir --upgrade -r /image-restoration/requirements.txt
COPY ./src /image-restoration/src
COPY ./alembic.ini /image-restoration/alembic.ini
COPY ./alembic /image-restoration/alembic
CMD ["uvicorn", "src:init_app", "--host", "0.0.0.0", "--port", "80"]
