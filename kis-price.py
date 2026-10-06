import os
import time
import requests
from flask import Flask, jsonify

app = Flask(__name__)

APP_KEY = os.environ.get("APP_KEY")
APP_SECRET = os.environ.get("APP_SECRET")

BASE_URL = "https://openapi.koreainvestment.com:9443"

# 발급받은 토큰을 메모리에 저장
ACCESS_TOKEN = None
TOKEN_EXPIRES_AT = 0


def get_access_token():
    global ACCESS_TOKEN, TOKEN_EXPIRES_AT

    # 기존 토큰이 아직 유효하면 재사용
    if ACCESS_TOKEN and time.time() < TOKEN_EXPIRES_AT:
        return ACCESS_TOKEN

    if not APP_KEY or not APP_SECRET:
        raise RuntimeError(
            "APP_KEY 또는 APP_SECRET 환경변수가 설정되어 있지 않습니다."
        )

    url = f"{BASE_URL}/oauth2/tokenP"

    headers = {
        "content-type": "application/json"
    }

    body = {
        "grant_type": "client_credentials",
        "appkey": APP_KEY,
        "appsecret": APP_SECRET
    }

    response = requests.post(
        url,
        headers=headers,
        json=body,
        timeout=10
    )

    response.raise_for_status()

    data = response.json()

    ACCESS_TOKEN = data["access_token"]

    # 한국투자증권 토큰의 실제 만료시간보다 여유 있게 재발급
    expires_in = int(data.get("expires_in", 86400))
    TOKEN_EXPIRES_AT = time.time() + max(expires_in - 300, 60)

    return ACCESS_TOKEN


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
        # 국내 종목코드는 숫자 6자리만 허용
        if not code.isdigit() or len(code) != 6:
            return jsonify({
                "status": "ERROR",
                "message": "종목코드는 숫자 6자리여야 합니다."
            }), 400

        token = get_access_token()

        url = (
            f"{BASE_URL}"
            "/uapi/domestic-stock/v1/quotations/inquire-price"
        )

        headers = {
            "content-type": "application/json; charset=utf-8",
            "authorization": f"Bearer {token}",
            "appkey": APP_KEY,
            "appsecret": APP_SECRET,
            "tr_id": "FHKST01010100",
            "custtype": "P"
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

        # 한국투자증권 API 자체 오류도 확인
        if data.get("rt_cd") != "0":
            return jsonify({
                "status": "ERROR",
                "message": data.get(
                    "msg1",
                    "한국투자증권 API 오류"
                ),
                "data": data
            }), 502

        return jsonify(data)

    except requests.exceptions.Timeout:
        return jsonify({
            "status": "ERROR",
            "message": "한국투자증권 API 응답 시간이 초과되었습니다."
        }), 504

    except requests.exceptions.RequestException as e:
        return jsonify({
            "status": "ERROR",
            "message": f"API 연결 오류: {str(e)}"
        }), 502

    except Exception as e:
        return jsonify({
            "status": "ERROR",
            "message": str(e)
        }), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(
        host="0.0.0.0",
        port=port
    )
