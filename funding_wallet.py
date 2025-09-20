# funding_wallet.py
import hashlib
import hmac
import time
import urllib.parse

import requests

from system.system import api_key, api_secret


def get_funding_assets(
        api_key: str,
        api_secret: str,
        asset: str = None,
        need_btc_valuation: bool = False
):
    """
    Получает список активов в Funding Wallet через POST-запрос.
    Эндпоинт: POST /sapi/v1/asset/get-funding-asset

    :param api_key: API-ключ Binance
    :param api_secret: Секретный ключ Binance
    :param asset: Опционально — конкретный актив (например, "USDT")
    :param need_btc_valuation: Нужна ли оценка в BTC (true/false)
    :return: Список активов или None в случае ошибки
    """
    base_url = "https://api.binance.com"
    endpoint = "/sapi/v1/asset/get-funding-asset"
    timestamp = int(time.time() * 1000)

    # Формируем тело POST-запроса (в query string для подписи!)
    params = {
        'timestamp': timestamp,
        'recvWindow': 5000
    }

    if asset:
        params['asset'] = asset
    if need_btc_valuation:
        params['needBtcValuation'] = 'true'
    else:
        params['needBtcValuation'] = 'false'

    # Подпись HMAC SHA256
    query_string = urllib.parse.urlencode(params)
    signature = hmac.new(
        api_secret.encode('utf-8'),
        query_string.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

    # Добавляем подпись к параметрам
    params['signature'] = signature

    headers = {
        'X-MBX-APIKEY': api_key
    }

    url = f"{base_url}{endpoint}"

    print(f"[DEBUG] POST запрос к: {url}")
    print(f"[DEBUG] Параметры: {params}")

    try:
        response = requests.post(url, headers=headers, data=params, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка сети или HTTP: {e}")
        return None

    try:
        data = response.json()
    except ValueError:
        print(f"❌ Не удалось распарсить JSON: {response.text}")
        return None

    if isinstance(data, dict) and data.get('code'):
        print(f"❌ Ошибка API Binance: {data.get('msg')}")
        return None

    return data


def display_funding_assets(assets_data):
    """
    Красиво выводит данные Funding Wallet в консоль.
    """
    if not assets_data:
        print("📭 Funding Wallet пуст или произошла ошибка.")
        return

    print("\n" + "=" * 70)
    print("💰 АКТИВЫ В FUNDING WALLET")
    print("=" * 70)
    for item in assets_data:
        asset_name = item.get('asset', 'N/A')
        free = item.get('free', '0')
        locked = item.get('locked', '0')
        freeze = item.get('freeze', '0')
        withdrawing = item.get('withdrawing', '0')
        btc_valuation = item.get('btcValuation', 'N/A')

        print(f"▸ Актив: {asset_name}")
        print(f"  Свободно: {free}")
        print(f"  Заблокировано: {locked}")
        print(f"  Заморожено: {freeze}")
        print(f"  Выводится: {withdrawing}")
        print(f"  Эквивалент в BTC: {btc_valuation}")
        print("-" * 50)


# Пример использования как отдельного скрипта
if __name__ == '__main__':
    # Импортируем ключи из вашего system.system
    try:
        from system.system import api_key, api_secret
    except ImportError:
        print("❌ Не удалось импортировать api_key и api_secret. Проверьте system/system.py")
        exit(1)

    print("📡 Получение списка активов из Funding Wallet...")

    # Можно указать конкретный актив, например: asset="USDT"
    # Или включить BTC-оценку: need_btc_valuation=True
    assets = get_funding_assets(
        api_key=api_key,
        api_secret=api_secret,
        asset=None,  # Все активы
        need_btc_valuation=True  # Показать эквивалент в BTC
    )

    display_funding_assets(assets)
