
import os
import requests
from bs4 import BeautifulSoup
from flask import Flask

app = Flask(__name__)

TARGET_URL = os.getenv(
    "TARGET_URL",
    "https://news.ycombinator.com"
)


@app.route("/")
def home():
    try:
        response = requests.get(TARGET_URL, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        if "news.ycombinator.com" in TARGET_URL:
            titles = soup.select(".titleline a")
        else:
            titles = soup.find_all(["h1", "h2"])

        items = "".join(
            f"<li>{title.get_text(strip=True)}</li>"
            for title in titles
        )

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Web Scraper</title>
        </head>
        <body>
            <h1>Web Scraper Results</h1>
            <p>Source: {TARGET_URL}</p>
            <ol>{items}</ol>
        </body>
        </html>
        """

    except Exception as e:
        return f"<h1>Scraping failed</h1><p>{e}</p>", 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
