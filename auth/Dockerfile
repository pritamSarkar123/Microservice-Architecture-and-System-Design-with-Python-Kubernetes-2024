FROM python:3.10-slim-bullseye

RUN apt-get update && apt-get install -y --no-install-recommends --no-install-suggests \
    build-essential postgresql-client \
    && pip install --no-cache-dir --upgrade pip 

WORKDIR /app

COPY ./requirements.txt /app

RUN pip install -r requirements.txt --no-cache-dir

COPY . /app

EXPOSE 5000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "5000"]

