FROM python:3.9

ENV PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip &&\
    pip install -r requirements.txt

COPY app app

CMD [ "python", "-m", "app" ]
