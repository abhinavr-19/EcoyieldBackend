from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
CORS(app)

BASE_URL = "https://enam.gov.in"
TRADE_URL = "https://enam.gov.in/web/Ajax_ctrl/trade_data_list"


def fetch_trade_data():
    session = requests.Session()

    # Step 1: Visit dashboard page to get session cookie
    session.get(
        "https://enam.gov.in/web/dashboard/trade-data",
        headers={"User-Agent": "Mozilla/5.0"}
    )

    # Step 2: Call AJAX endpoint with same session
    headers = {
        "User-Agent": "Mozilla/5.0",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": "https://enam.gov.in/web/dashboard/trade-data",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    }

    payload = {
        "language": "en",
        "page": "1"
    }

    response = session.post(
        TRADE_URL,
        data=payload,
        headers=headers,
        timeout=15
    )

    response.raise_for_status()
    return response.text


def parse_html(html):
    soup = BeautifulSoup(html, "html.parser")
    rows = soup.find_all("tr")

    results = []

    for row in rows:
        cols = row.find_all("td")
        if len(cols) >= 6:
            results.append({
                "state": cols[0].get_text(strip=True),
                "mandi": cols[1].get_text(strip=True),
                "commodity": cols[2].get_text(strip=True),
                "min_price": cols[3].get_text(strip=True),
                "modal_price": cols[4].get_text(strip=True),
                "max_price": cols[5].get_text(strip=True),
            })

    return results


@app.route("/api/prices", methods=["GET"])
def get_prices():
    search_query = request.args.get("search", "").strip().lower()

    try:
        html = fetch_trade_data()
        data = parse_html(html)

        if search_query:
            data = [
                item for item in data
                if search_query in item["commodity"].lower()
            ]

        return jsonify({
            "total_records": len(data),
            "search_query": search_query if search_query else None,
            "data": data
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/")
def home():
    return jsonify({"status": "eNAM Price API Running 🚀"})


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)