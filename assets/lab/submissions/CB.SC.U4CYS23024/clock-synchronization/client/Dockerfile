# Base image with Python
FROM python:3.12-slim

WORKDIR /app
COPY client.py .

# Unbuffered output so logs appear immediately; local time zone for readable clocks
ENV PYTHONUNBUFFERED=1
ENV TZ=Asia/Kolkata

# Clients listen for the master's requests on this port
EXPOSE 5000

CMD ["python", "client.py"]
