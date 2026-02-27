from flask import Flask, jsonify
from flask_cors import CORS
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import os

app = Flask(__name__)
CORS(app)

def scrape_enam():
    options = webdriver.ChromeOptions()

    # 👇 IMPORTANT for Docker (Railway)
    options.binary_location = "/usr/bin/chromium"

    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")

    driver = webdriver.Chrome(options=options)

    driver.get("https://enam.gov.in/web/dashboard/trade-data")
    time.sleep(5)

    all_data = []

    while True:
        rows = driver.find_elements(By.XPATH, "//table/tbody/tr")

        for row in rows:
            cols = row.find_elements(By.TAG_NAME, "td")
            if len(cols) >= 6:
                all_data.append({
                    "state": cols[0].text.strip(),
                    "mandi": cols[1].text.strip(),
                    "commodity": cols[2].text.strip(),
                    "min_price": cols[3].text.strip(),
                    "modal_price": cols[4].text.strip(),
                    "max_price": cols[5].text.strip(),
                })

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
    return "eNAM Price API Running 🚀"


@app.route("/api/prices", methods=["GET"])
def get_prices():
    data = scrape_enam()
    return jsonify({
        "total_records": len(data),
        "data": data
    })


# ✅ Production-safe run config
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)