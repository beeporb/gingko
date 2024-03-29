FROM python:latest

WORKDIR /src/quasar

COPY . .

RUN pip install -r requirements.txt

ENTRYPOINT [ "python", "watch.py" ]