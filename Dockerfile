FROM python:3.9-slim-bullseye

WORKDIR app

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY streamlit.py streamlit.py

CMD ["streamlit", "run", "streamlit.py", "--server.port", "5113"]
