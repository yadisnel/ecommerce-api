FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

COPY . /app/app
RUN pip install -r /app/app/requirements.txt
WORKDIR /app/app
