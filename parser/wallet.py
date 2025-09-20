import hashlib
import hmac
import time
import urllib.parse

import requests
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from proxy import setup_proxy
from system.system import api_key, api_secret, user, password, ip, port, router


def get_wallet_balance(api_key, secret_key, quote_asset="USDT"):
    """
    Получает баланс по всем кошелькам Binance в указанной валюте.
    Эндпоинт: GET /sapi/v1/asset/wallet/balance
    """
    setup_proxy(user=user, password=password, ip=ip, port=port)

    base_url = "https://api.binance.com"  # ❗️ УБРАЛИ ЛИШНИЕ ПРОБЕЛЫ
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
        return response.json()
    else:
        print(f"❌ Ошибка API: {response.status_code} — {response.text}")
        return None


def get_funding_assets(api_key, secret_key, asset: str = None, need_btc_valuation: bool = False):
    """
    Получает список активов в Funding Wallet через POST.
    Эндпоинт: POST /sapi/v1/asset/get-funding-asset
    """
    setup_proxy(user=user, password=password, ip=ip, port=port)

    base_url = "https://api.binance.com"  # ❗️ УБРАЛИ ЛИШНИЕ ПРОБЕЛЫ
    endpoint = "/sapi/v1/asset/get-funding-asset"
    timestamp = int(time.time() * 1000)

    params = {
        'timestamp': timestamp,
        'recvWindow': 5000,
        'needBtcValuation': 'true' if need_btc_valuation else 'false'
    }

    if asset:
        params['asset'] = asset

    query_string = urllib.parse.urlencode(params)
    signature = hmac.new(secret_key.encode(), query_string.encode(), hashlib.sha256).hexdigest()
    params['signature'] = signature  # Подпись в теле POST

    headers = {'X-MBX-APIKEY': api_key}
    url = f"{base_url}{endpoint}"

    print(f"[DEBUG] POST запрос к: {url}")

    try:
        response = requests.post(url, headers=headers, data=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"❌ Ошибка Funding: {e}")
        return None


@router.message(Command("balance"))
async def balance(message: Message):
    """Отправляет пользователю баланс по кошелькам и Funding Wallet"""
    await message.answer("⏳ Получаю информацию о балансе с Binance...")

    # Получаем баланс по кошелькам
    balances = get_wallet_balance(api_key, api_secret, quote_asset="USDT")
    if not balances:
        await message.answer("❌ Не удалось получить баланс кошельков. Проверьте API-ключи и подключение.")
        return

    # Формируем сообщение по кошелькам
    text = "📊 <b>Баланс по кошелькам (в USDT):</b>\n\n"
    for wallet in balances:
        status = "✅ активен" if wallet['activate'] else "⛔ не активен"
        text += f"• <b>{wallet['walletName']}</b>: {wallet['balance']} USDT ({status})\n"

    # Получаем Funding активы
    funding_assets = get_funding_assets(api_key, api_secret, need_btc_valuation=False)
    if funding_assets:
        text += "\n💼 <b>Funding Wallet:</b>\n\n"
        for asset in funding_assets:
            free = asset.get('free', '0')
            locked = asset.get('locked', '0')
            freeze = asset.get('freeze', '0')
            asset_name = asset.get('asset', 'N/A')
            text += f"• <b>{asset_name}</b>: свободно {free}, заблокировано {locked}, заморожено {freeze}\n"
    else:
        text += "\n⚠️ Не удалось получить данные Funding Wallet."

    # Отправляем пользователю
    try:
        await message.answer(text, parse_mode="HTML")
    except Exception as e:
        print(f"Ошибка отправки сообщения: {e}")
        await message.answer("❌ Не удалось отправить сообщение — слишком длинное. Проверьте логи.")


def register_commands_handler():
    # router.register.message_handler(balance)
    router.message.register(balance)
