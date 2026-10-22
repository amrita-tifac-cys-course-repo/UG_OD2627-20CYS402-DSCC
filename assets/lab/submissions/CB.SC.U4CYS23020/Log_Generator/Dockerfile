FROM python:3.13-slim

RUN mkdir -p /data && printf 'import time\nfrom datetime import datetime, timezone\nwhile True:\n    ts = datetime.now(timezone.utc).isoformat()\n    with open("/data/log.txt", "a") as f:\n        f.write(ts + "\\n")\n    print("Logged:", ts)\n    time.sleep(5)\n' > /app.py

CMD ["python", "/app.py"]