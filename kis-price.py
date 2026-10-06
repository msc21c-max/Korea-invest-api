import os
import requests
from flask import Flask, jsonify

app = Flask(__name__)

APP_KEY = os.environ.get("APP_KEY")
APP_SECRET = os.environ.get("APP_SECRET")

BASE_URL = "https://openapi.koreainvestment.com:9443"

# 자주 확인할 종목
STOCKS = {
    "삼성전자": "005930",
    "두산에너빌리티": "034020",
    "현대로템": "064350",
    "LS ELECTRIC": "010120",
    "HD현대일렉트릭": "267260",
    "한화오션": "042660",
}


def get_access_token():
    if not APP_KEY or not APP_SECRET:
        raise Exception("APP_KEY 또는 APP_SECRET이 설정되지 않았습니다.")

    url = f"{BASE_URL}/oauth2/tokenP"

    body = {
        "grant_type": "client_credentials",
        "appkey": APP_KEY,
        "appsecret": APP_SECRET,
    }

    response = requests.post(url, json=body, timeout=10)
    response.raise_for_status()

    data = response.json()
    return data["access_token"]


def get_stock_price(code):
    token = get_access_token()

    url = (
        f"{BASE_URL}/uapi/domestic-stock/v1/quotations/"
        f"inquire-price"
    )

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
        raise Exception(
            data.get("msg1", "한국투자증권 API 오류")
        )

    output = data.get("output", {})

    return {
        "code": code,
        "price": output.get("stck_prpr"),
        "change": output.get("prdy_vrss"),
        "change_rate": output.get("prdy_ctrt"),
        "open": output.get("stck_oprc"),
        "high": output.get("stck_hgpr"),
        "low": output.get("stck_lwpr"),
        "volume": output.get("acml_vol"),
    }


@app.route("/")
def home():
    return jsonify({
        "service": "Korea Invest API",
        "status": "OK",
        "usage": {
            "price_by_code": "/price/005930",
            "price_by_name": "/stock/삼성전자",
            "all_watchlist": "/watchlist",
        }
    })


@app.route("/price/<code>")
def price_by_code(code):
    try:
        result = get_stock_price(code)
        return jsonify(result)

    except Exception as e:
        return jsonify({
            "error": str(e),
            "code": code,
        }), 500


@app.route("/stock/<name>")
def price_by_name(name):
    try:
        code = STOCKS.get(name)

        if not code:
            return jsonify({
                "error": "등록되지 않은 종목명입니다.",
                "name": name,
            }), 404

        result = get_stock_price(code)
        result["name"] = name

        return jsonify(result)

    except Exception as e:
        return jsonify({
            "error": str(e),
            "name": name,
        }), 500


@app.route("/watchlist")
def watchlist():
    results = []

    for name, code in STOCKS.items():
        try:
            result = get_stock_price(code)
            result["name"] = name
            results.append(result)

        except Exception as e:
            results.append({
                "name": name,
                "code": code,
                "error": str(e),
            })

    return jsonify(results)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(
        host="0.0.0.0",
        port=port,
        debug=False,
    )
