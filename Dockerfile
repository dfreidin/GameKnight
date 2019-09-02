FROM python:3.7-alpine

RUN mkdir /app

COPY ./flask /app
COPY ./requirements.txt /app

RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev
RUN python -m pip install --no-cache-dir -r /app/requirements.txt

ENV FLASK_APP /app/app.py
ENV PYTHONPATH "${PYTHONPATH}:/app"

EXPOSE 5000

CMD ["flask", "run", "--host", "0.0.0.0"]