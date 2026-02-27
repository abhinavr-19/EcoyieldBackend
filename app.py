from flask import Flask, jsonify, request
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

ENAM_API = "https://enam.gov.in/web/dashboard/trade-data"

@app.route("/")
def home():
    return jsonify({
        "status": "eNAM Price API Running 🚀",
        "usage": "/api/prices?search=tomato"
    })


@app.route("/api/prices", methods=["GET"])
def get_prices():
    search_query = request.args.get("search", "").strip().lower()

    try:
        # Direct request to eNAM backend API
        response = requests.get(
            "https://enam.gov.in/web/dashboard/trade-data?format=json",
            timeout=10
        )

        data = response.json()

        results = []

        for item in data.get("data", []):
            commodity = item.get("commodity", "").lower()

            if search_query:
                if search_query not in commodity:
                    continue

            results.append({
                "state": item.get("state"),
                "mandi": item.get("mandi"),
                "commodity": item.get("commodity"),
                "min_price": item.get("min_price"),
                "modal_price": item.get("modal_price"),
                "max_price": item.get("max_price"),
            })

        return jsonify({
            "total_records": len(results),
            "search_query": search_query if search_query else None,
            "data": results
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)