FROM python:3.11-slim

COPY src /app
ADD requirements.txt /app

WORKDIR /app
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

CMD exec uvicorn --host 0.0.0.0 server:fastapi_app --port 8000 --log-config uvicorn-logging.yml --reload
EXPOSE 8000