from flask import Flask
import os
import psycopg2

app = Flask(__name__)

@app.route("/")
def home():
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            dbname=os.getenv("DB_NAME")
        )

        conn.close()
        return "Database Connection Successful!"

    except Exception as e:
        return f"Database Connection Failed!<br>{e}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)