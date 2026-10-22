import os
from flask import Flask

app = Flask(__name__)

UPLOAD_DIR = os.environ.get("UPLOAD_DIR", "/app/uploads")
APP_PORT = int(os.environ.get("APP_PORT", 8000))


@app.route("/")
def home():
    files = os.listdir(UPLOAD_DIR)
    links = "".join(f'<li><a href="/files/{f}">{f}</a></li>' for f in files)
    return f"<h2>Shared Files</h2><ul>{links}</ul>"


@app.route("/files/<filename>")
def view_file(filename):
    with open(os.path.join(UPLOAD_DIR, filename)) as f:
        return f"<pre>{f.read()}</pre>"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=APP_PORT)
    