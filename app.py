from flask import Flask, jsonify, request
from flask_cors import CORS
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os

app = Flask(__name__)
CORS(app)


def scrape_enam(search_query=None):
    options = webdriver.ChromeOptions()

    # Required for Railway/Docker
    options.binary_location = "/usr/bin/chromium"
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")

    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 15)

    driver.get("https://enam.gov.in/web/dashboard/trade-data")

    # Wait until table loads
    wait.until(EC.presence_of_element_located((By.XPATH, "//table/tbody/tr")))

    all_data = []

    while True:
        rows = driver.find_elements(By.XPATH, "//table/tbody/tr")

        for row in rows:
            cols = row.find_elements(By.TAG_NAME, "td")
            if len(cols) >= 6:
                commodity_name = cols[2].text.strip()

                # 🔥 Filter during scraping (more efficient)
                if search_query:
                    if search_query.lower() not in commodity_name.lower():
                        continue

                all_data.append({
                    "state": cols[0].text.strip(),
                    "mandi": cols[1].text.strip(),
                    "commodity": commodity_name,
                    "min_price": cols[3].text.strip(),
                    "modal_price": cols[4].text.strip(),
                    "max_price": cols[5].text.strip(),
                })

        # Handle pagination
        try:
            next_button = driver.find_element(By.XPATH, "//a[text()='Next']")
            if "disabled" in next_button.get_attribute("class"):
                break

            next_button.click()
            time.sleep(2)

        except:
            break

    driver.quit()
    return all_data


@app.route("/")
def home():
    return jsonify({
        "status": "eNAM Price API Running 🚀",
        "usage": "/api/prices?search=tomato"
    })


@app.route("/api/prices", methods=["GET"])
def get_prices():
    search_query = request.args.get("search", "").strip()

    data = scrape_enam(search_query if search_query else None)

    return jsonify({
        "total_records": len(data),
        "search_query": search_query if search_query else None,
        "data": data
    })


# Production run config
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)