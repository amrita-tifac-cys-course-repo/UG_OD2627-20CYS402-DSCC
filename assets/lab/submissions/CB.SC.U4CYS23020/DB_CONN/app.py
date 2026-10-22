import os
import psycopg2
from http.server import BaseHTTPRequestHandler, HTTPServer

DB_HOST = os.environ.get("DB_HOST", "db.example.com")
DB_PORT = os.environ.get("DB_PORT", "5432")
DB_USER = os.environ.get("DB_USER", "dummy_user")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "dummy_password")
DB_NAME = os.environ.get("DB_NAME", "dummy_db")


def check_db_connection():
    
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            dbname=DB_NAME,
            connect_timeout=5,
        )
        conn.close()
        return "success"
    except Exception as e:
        return f"failed: {e}"


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        status = check_db_connection()
        message = f"DB host: {DB_HOST}:{DB_PORT} | DB name: {DB_NAME} | Connection: {status}\n"
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(message.encode())


if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", 8080), Handler)
    print("Server running on 0.0.0.0:8080")
    server.serve_forever()