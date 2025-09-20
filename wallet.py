import hashlib
import hmac
import time
import urllib.parse

import requests


def get_wallet_balance(api_key, secret_key, quote_asset="USDT"):
    """
    Получает баланс по всем кошелькам Binance в указанной валюте (по умолчанию USDT).
    Эндпоинт: GET /sapi/v1/asset/wallet/balance
    """
    base_url = "https://api.binance.com"  # ✅ ИСПРАВЛЕНО
    endpoint = "/sapi/v1/asset/wallet/balance"
    timestamp = int(time.time() * 1000)

    params = {
        'timestamp': timestamp,
        'recvWindow': 5000
    }

    if quote_asset:
        params['quoteAsset'] = quote_asset

    query_string = urllib.parse.urlencode(params)
    signature = hmac.new(secret_key.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()

    headers = {
        'X-MBX-APIKEY': api_key
    }

    url = f"{base_url}{endpoint}?{query_string}&signature={signature}"
    print(f"[DEBUG] Запрос к: {url}")

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка сети или HTTP: {e}")
        return None

    if response.status_code == 200:
        data = response.json()
        print(f"\n--- Баланс в {quote_asset} по всем кошелькам ---")
        for wallet in data:
            status = 'активен' if wallet['activate'] else 'не активен'
            print(f"▸ {wallet['walletName']}: {wallet['balance']} {quote_asset} ({status})")
        return data
    else:
        print(f"❌ Ошибка API: {response.status_code} — {response.text}")
        return None


def get_funding_assets(api_key, secret_key):
    """
    Получает список активов в Funding Wallet.
    Эндпоинт: GET /sapi/v1/asset/get-funding-asset
    """
    base_url = "https://api.binance.com"  # ✅ ИСПРАВЛЕНО
    endpoint = "/sapi/v1/asset/get-funding-asset"
    timestamp = int(time.time() * 1000)
    params = {'timestamp': timestamp}
    query_string = urllib.parse.urlencode(params)
    signature = hmac.new(secret_key.encode(), query_string.encode(), hashlib.sha256).hexdigest()
    url = f"{base_url}{endpoint}?{query_string}&signature={signature}"
    headers = {'X-MBX-APIKEY': api_key}

    print(f"[DEBUG] Funding запрос к: {url}")

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка при получении Funding активов: {e}")
        return None

    try:
        return response.json()
    except ValueError:
        print(f"❌ Не удалось распарсить JSON: {response.text}")
        return None


# Пример использования
if __name__ == '__main__':
    from system.system import api_key, api_secret

    print("📡 Получение баланса по всем кошелькам Binance...")
    balances = get_wallet_balance(api_key, api_secret, quote_asset="USDT")

    if balances is None:
        print("⚠️  Не удалось получить данные. Проверьте ключи, интернет и настройки API.")
    else:
        # Уже выводится внутри функции
        pass

    print("\n" + "=" * 60)
    balances_funding = get_funding_assets(api_key, api_secret)
    if balances_funding:
        print("\n--- Активы в Funding Wallet ---")
        for asset in balances_funding:
            free = asset.get('free', '0')
            locked = asset.get('locked', '0')
            asset_name = asset.get('asset', 'N/A')
            print(f"▸ {asset_name}: свободно {free}, заблокировано {locked}")
    else:
        print("⚠️  Не удалось получить список активов Funding Wallet.")
