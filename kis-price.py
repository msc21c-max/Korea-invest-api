import requests
import os
# 한국투자증권 Open API
BASE_URL = "https://openapi.koreainvestment.com:9443"

# 아래 두 곳은 나중에 본인의 키로 입력합니다.
APP_KEY = "PSMWL1TLxYcAECT8YR1UYXt4d6ThjIpIpsU6"
APP_SECRET = "Q8vqn4NgFm82zuEsazwhvoiKhYhXpnbjBAj1szsie9Q/buVIqd4iQBGLHlJMp+AvWJ6uRirv4u4p3K9x8saCIyuGnm22TWzc9rpyXN7He41pccpvFTt5V+NI/G9BE+pDFtfQe8YIQKwwV2j7ZqfGJGrHhRpcfRomrMUKsUe9q3dFYAcZTLA="


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


def get_price(token, stock_code):
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
        "FID_INPUT_ISCD": stock_code
    }

    res = requests.get(url, headers=headers, params=params)
    res.raise_for_status()

    data = res.json()

    if data.get("rt_cd") != "0":
        print("API 오류:", data)
        return

    output = data["output"]

    print(
        stock_code,
        "현재가:", output.get("stck_prpr"),
        "등락률:", output.get("prdy_ctrt"),
        "거래량:", output.get("acml_vol")
    )
    

if __name__ == "__main__":
    token = get_access_token()

    stocks = {
        "삼성전자": "005930",
        "현대로템": "064350",
        "두산에너빌리티": "034020",
        "한화오션": "042660",
        "LS ELECTRIC": "010120",
        "원익IPS": "240810",
        "주성엔지니어링": "036930",
        "이오테크닉스": "039030"
    }

    for name, code in stocks.items():
        print("\n", name)
        get_price(token, code)
      
