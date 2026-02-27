from flask import Flask, jsonify
from flask_cors import CORS
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

app = Flask(__name__)
CORS(app)

def scrape_enam():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")   # 🔥 run without opening browser
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    driver.get("https://enam.gov.in/web/dashboard/trade-data")
    time.sleep(5)

    all_data = []

    while True:
        rows = driver.find_elements(By.XPATH, "//table/tbody/tr")

        for row in rows:
            cols = row.find_elements(By.TAG_NAME, "td")
            if len(cols) >= 6:
                all_data.append({
                    "state": cols[0].text,
                    "mandi": cols[1].text,
                    "commodity": cols[2].text,
                    "min_price": cols[3].text,
                    "modal_price": cols[4].text,
                    "max_price": cols[5].text,
                })

        try:
            next_button = driver.find_element(By.XPATH, "//a[text()='Next']")
            if "disabled" in next_button.get_attribute("class"):
                break
            next_button.click()
            time.sleep(3)
        except:
            break

    driver.quit()
    return all_data


@app.route("/api/prices", methods=["GET"])
def get_prices():
    data = scrape_enam()
    return jsonify({
        "total_records": len(data),
        "data": data
    })


if __name__ == "__main__":
    app.run(debug=True, port=5000)