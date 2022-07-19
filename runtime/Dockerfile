FROM python:3.9-slim-bullseye

WORKDIR /opt

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY custom_module.py context.py app.py ./

CMD ["python3", "app.py"]
