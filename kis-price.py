import os
import requests
from flask import Flask, jsonify

app = Flask(__name__)

APP_KEY = os.environ.get("APP_KEY")
APP_SECRET = os.environ.get("APP_SECRET")

KIS_BASE_URL = "https://openapi.koreainvestment.com:9443"


def get_access_token():
    if not APP_KEY or not APP_SECRET:
        raise RuntimeError("APP_KEY 또는 APP_SECRET 환경변수가 없습니다.")

    url = f"{KIS_BASE_URL}/oauth2/tokenP"
    body = {
        "grant_type": "client_credentials",
        "appkey": APP_KEY,
        "appsecret": APP_SECRET,
    }

    response = requests.post(url, json=body, timeout=10)
    response.raise_for_status()
    return response.json()["access_token"]


def get_price(code):
    token = get_access_token()

    url = f"{KIS_BASE_URL}/uapi/domestic-stock/v1/quotations/inquire-price"

    headers = {
        "authorization": f"Bearer {token}",
        "appkey": APP_KEY,
        "appsecret": APP_SECRET,
        "tr_id": "FHKST01010100",
        "custtype": "P",
    }

    params = {
        "FID_COND_MRKT_DIV_CODE": "J",
        "FID_INPUT_ISCD": code,
    }

    response = requests.get(
        url,
        headers=headers,
        params=params,
        timeout=10,
    )
    response.raise_for_status()

    data = response.json()

    if data.get("rt_cd") != "0":
        raise RuntimeError(data.get("msg1", "KIS API 조회 실패"))

    output = data.get("output", {})

    return {
        "code": code,
        "price": output.get("stck_prpr"),
        "change": output.get("prdy_vrss"),
        "change_rate": output.get("prdy_ctrt"),
    }


@app.route("/")
def home():
    return jsonify({
        "status": "ok",
        "service": "korea-invest-api",
        "usage": "/price/005930",
    })


@app.route("/price/<code>")
def price(code):
    try:
        if not code.isdigit() or len(code) != 6:
            return jsonify({
                "error": "종목코드는 6자리 숫자여야 합니다."
            }), 400

        return jsonify(get_price(code))

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8080"))
    app.run(host="0.0.0.0", port=port)
