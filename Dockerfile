# https://hub.docker.com/_/python
FROM python:3.10-slim-bullseye

ENV PYTHONUNBUFFERED True
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

# Install poetry
RUN pip install poetry

RUN poetry install

CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]