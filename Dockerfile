FROM python:3

ARG PORT=8000

RUN mkdir /app
WORKDIR /app
COPY . /app

RUN pip install -r requirements.txt

ENV GUNICORN_CMD_ARGS="--bind=0:${PORT} --worker-class=gthread --threads=10"

CMD ["gunicorn", "seventweets:app"]
