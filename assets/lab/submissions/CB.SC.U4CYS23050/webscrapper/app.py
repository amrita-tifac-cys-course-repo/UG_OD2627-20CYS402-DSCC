import os
import requests
from bs4 import BeautifulSoup

# Read TARGET_URL from the environment
target_url = os.getenv("TARGET_URL", "https://news.ycombinator.com")

try:
    # Fetch the webpage
    response = requests.get(target_url)
    response.raise_for_status()

    # Parse the HTML
    soup = BeautifulSoup(response.text, "html.parser")

    print(f"\nScraping: {target_url}\n")

    # If Hacker News, scrape article titles
    if "news.ycombinator.com" in target_url:
        titles = soup.select(".titleline a")

        print("Article Titles:\n")
        for i, title in enumerate(titles, 1):
            print(f"{i}. {title.get_text(strip=True)}")

    else:
        # For other websites, print H1 and H2 headings
        titles = soup.find_all(["h1", "h2"])

        print("Headings:\n")
        for i, title in enumerate(titles, 1):
            print(f"{i}. {title.get_text(strip=True)}")

except Exception as e:
    print(f"Error fetching or parsing the URL: {e}")