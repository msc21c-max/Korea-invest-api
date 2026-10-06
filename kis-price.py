import os
import requests
from flask import Flask, jsonify

app = Flask(__name__)

APP_KEY = os.environ.get("APP_KEY")
APP_SECRET = os.environ.get("APP_SECRET")

BASE_URL = "https://openapi.koreainvestment.com:9443"


def get_access_token():
    url = f"{BASE_URL}/oauth2/tokenP"

    headers = {
        "content-type": "application/json"
    }

    body = {
        "grant_type": "client_credentials",
        "appkey": APP_KEY,
        "appsecret": APP_SECRET
    }

    response = requests.post(url, headers=headers, json=body, timeout=10)
    response.raise_for_status()

    return response.json()["access_token"]


@app.route("/")
def home():
    return jsonify({
        "service": "Korea Investment API",
        "status": "OK",
        "usage": "/price/005930"
    })


@app.route("/price/<code>")
def get_price(code):
    try:
        token = get_access_token()

        url = f"{BASE_URL}/uapi/domestic-stock/v1/quotations/inquire-price"

        headers = {
            "content-type": "application/json; charset=utf-8",
            "authorization": f"Bearer {token}",
            "appkey": APP_KEY,
            "appsecret": APP_SECRET,
            "tr_id": "FHKST01010100"
        }

        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": code
        }

        response = requests.get(
            url,
            headers=headers,
            params=params,
            timeout=10
        )

        response.raise_for_status()
        data = response.json()

        return jsonify(data)

    except Exception as e:
        return jsonify({
            "status": "ERROR",
            "message": str(e)
        }), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
