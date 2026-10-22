FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

ENV DB_HOST=db.example.com \
    DB_PORT=1234 \
    DB_USER=user \
    DB_PASSWORD=pass \
    DB_NAME=db

EXPOSE 8080

CMD ["python", "app.py"]
