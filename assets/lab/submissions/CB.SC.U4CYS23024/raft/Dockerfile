FROM python:3.12-slim

WORKDIR /app
COPY raft_node.py client.py ./

ENV PYTHONUNBUFFERED=1
ENV TZ=Asia/Kolkata

EXPOSE 8000
# Default role is a Raft node; the client service overrides this
CMD ["python", "raft_node.py"]
