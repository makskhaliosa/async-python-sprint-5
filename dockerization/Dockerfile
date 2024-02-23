FROM python:3.11

WORKDIR /app

COPY requirements.txt /app/requirements.txt

RUN python -m pip install --upgrade pip

RUN pip install -r requirements.txt --no-cache-dir

COPY alembic.ini /app/alembic.ini
COPY migrations /app/migrations
COPY src /app/src
COPY .env /app/.env
COPY start_app.sh /app/start_app.sh

CMD ["python", "src/main.py"]
