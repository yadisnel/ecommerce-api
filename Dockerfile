FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

COPY . /app/app
RUN pip install -r /app/app/requirements.txt
RUN apt-get update -y
RUN apt install libgl1-mesa-glx -y
WORKDIR /app/app
