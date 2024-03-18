# # https://hub.docker.com/_/python
# FROM python:3.10-slim-bullseye

# ENV PYTHONUNBUFFERED True
# ENV APP_HOME /app
# WORKDIR $APP_HOME
# COPY . ./

# # Install poetry
# RUN pip install poetry

# RUN poetry install

# CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]

# https://hub.docker.com/_/python
FROM python:3.10-slim-bullseye as builder

ENV PYTHONUNBUFFERED True
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

# Install poetry
RUN pip install poetry

# Install dependencies
RUN poetry export -f requirements.txt --output requirements.txt
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /wheels -r requirements.txt

# Stage 2
FROM python:3.10-slim-bullseye

ENV APP_HOME /app
WORKDIR $APP_HOME

# Install dependencies
COPY --from=builder /wheels /wheels
COPY --from=builder /app/requirements.txt .
RUN pip install --no-cache-dir --no-index --find-links=/wheels -r requirements.txt

# Copy the rest of the application
COPY . ./

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]