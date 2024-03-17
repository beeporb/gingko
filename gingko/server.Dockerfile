FROM python:latest

WORKDIR /src/quasar

COPY . .

RUN pip install -r requirements.txt

ENTRYPOINT [ "uvicorn", "server:api", "--host", "0.0.0.0", "--port", "8080" ]