FROM python:3.11
WORKDIR /app
RUN pip install poetry
ENV POETRY_VIRTUALENVS_CREATE=false
COPY . /app
RUN poetry install
