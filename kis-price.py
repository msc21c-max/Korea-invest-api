import os
import requests

APP_KEY = os.environ["APP_KEY"]
APP_SECRET = os.environ["APP_SECRET"]

BASE_URL = "https://openapi.koreainvestment.com:9443"


# 1. 토큰은 한 번만 발급
def get_access_token():
    url = f"{BASE_URL}/oauth2/tokenP"

    body = {
        "grant_type": "client_credentials",
        "appkey": APP_KEY,
        "appsecret": APP_SECRET
    }

    res = requests.post(url, json=body)
    res.raise_for_status()

    return res.json()["access_token"]


# 2. 발급받은 토큰으로 여러 종목 조회
def get_stock_price(stock_code, access_token):
    url = f"{BASE_URL}/uapi/domestic-stock/v1/quotations/inquire-price"

    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "authorization": f"Bearer {access_token}",
        "appkey": APP_KEY,
        "appsecret": APP_SECRET,
        "tr_id": "FHKST01010100"
    }

    params = {
        "FID_COND_MRKT_DIV_CODE": "J",
        "FID_INPUT_ISCD": stock_code
    }

    res = requests.get(url, headers=headers, params=params)
    res.raise_for_status()

    return res.json()


# 3. 여기서 딱 한 번 토큰 발급
access_token = get_access_token()


# 4. 여러 종목은 같은 토큰 사용
stock_codes = [
    "005930",  # 삼성전자
]

for code in stock_codes:
    try:
        result = get_stock_price(code, access_token)
        print(code, result)

    except Exception as e:
        print(code, "조회 오류:", e)
