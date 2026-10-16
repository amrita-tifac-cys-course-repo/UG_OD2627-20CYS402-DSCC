# Base image with Python
FROM python:3.12-slim

WORKDIR /app
COPY master.py .

# Unbuffered output so logs appear immediately; local time zone for readable clocks
ENV PYTHONUNBUFFERED=1
ENV TZ=Asia/Kolkata

# Time server port
EXPOSE 5000

CMD ["python", "master.py"]
