FROM python:3.12-slim


WORKDIR /app


COPY pyproject.toml poetry.lock ./


RUN pip install poetry && poetry install --no-dev


COPY src ./src


ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app


CMD ["poetry", "run", "python", "src/app.py"]