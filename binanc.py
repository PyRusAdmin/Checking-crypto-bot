# # -*- coding: utf-8 -*-
# from datetime import datetime
#
# from binance.client import Client
#
# from proxy import setup_proxy
# from system.system import api_secret, api_key, user, password, ip, port
#
#
# def parse_binance():
#     setup_proxy(user=user, password=password, ip=ip, port=port)
#
#     client = Client(api_key=api_key, api_secret=api_secret)
#
#     transfers = client.get_user_asset_transfer_history()
#
#     for t in transfers:
#         print(
#             f"🕒 {datetime.fromtimestamp(t['timestamp'] / 1000)} | "
#             f"🪙 {t['asset']} {t['amount']} | "
#             f"🔀 {t['type']} | "
#             f"📤 {t.get('fromAccountType', '—')} → 📥 {t.get('toAccountType', '—')}"
#         )
#
#     account = client.get_account()
#
#     for bal in account["balances"]:
#         if float(bal['free']) > 0.0:
#             print(f"{bal['asset'].ljust(10, '-')} {float(bal['free']):.3f}")
#
#
# if __name__ == '__main__':
#     parse_binance()

# import hashlib
# import hmac
# import time
# import requests
#
# from proxy import setup_proxy
# from system.system import user, password, ip, port, api_key, api_secret
#
# # Исправлено: убран лишний пробел
# BASE_URL = 'https://api.binance.com'
#
#
# def sign_request(params, secret):
#     """Подпись параметров запроса HMAC SHA256"""
#     query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
#     signature = hmac.new(secret.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()
#     return signature
#
#
# def get_spot_balance():
#     """Получить текущий баланс спотового аккаунта"""
#     setup_proxy(user=user, password=password, ip=ip, port=port)
#
#     endpoint = '/api/v3/account'
#     params = {
#         'timestamp': int(time.time() * 1000)
#     }
#     params['signature'] = sign_request(params, api_secret)
#
#     headers = {
#         'X-MBX-APIKEY': api_key
#     }
#
#     url = BASE_URL + endpoint
#     response = requests.get(url, headers=headers, params=params)
#
#     if response.status_code == 200:
#         data = response.json()
#         balances = data['balances']
#         print("=== Текущий баланс спот-аккаунта ===")
#         for asset in balances:
#             free = float(asset['free'])
#             locked = float(asset['locked'])
#             if free > 0 or locked > 0:
#                 print(f"{asset['asset']}: свободно {free}, заблокировано {locked}")
#     else:
#         print("❌ Ошибка получения баланса:", response.text)
#
# def get_transfer_direction(transfer_type):
#     """Возвращает направление перевода на основе типа"""
#     mapping = {
#         'MAIN_UMFUTURE': ('SPOT', 'USDT_FUTURE'),
#         'UMFUTURE_MAIN': ('USDT_FUTURE', 'SPOT'),
#         'MAIN_CMFUTURE': ('SPOT', 'COINM_FUTURE'),
#         'CMFUTURE_MAIN': ('COINM_FUTURE', 'SPOT'),
#         'MAIN_MARGIN': ('SPOT', 'MARGIN'),
#         'MARGIN_MAIN': ('MARGIN', 'SPOT'),
#         'MAIN_FUNDING': ('SPOT', 'FUNDING'),
#         'FUNDING_MAIN': ('FUNDING', 'SPOT'),
#         'MARGIN_FUNDING': ('MARGIN', 'FUNDING'),
#         'FUNDING_MARGIN': ('FUNDING', 'MARGIN'),
#     }
#     return mapping.get(transfer_type, ('-', '-'))
#
# def get_internal_transfers():
#     """Получить историю внутренних переводов по всем основным типам"""
#     setup_proxy(user=user, password=password, ip=ip, port=port)
#
#     # Список типов переводов для запроса
#     transfer_types = [
#         'MAIN_UMFUTURE',    # Spot → USDT Futures
#         'UMFUTURE_MAIN',    # USDT Futures → Spot
#         'MAIN_CMFUTURE',    # Spot → COIN-M Futures
#         'CMFUTURE_MAIN',    # COIN-M Futures → Spot
#         'MAIN_MARGIN',      # Spot → Margin
#         'MARGIN_MAIN',      # Margin → Spot
#         'MAIN_FUNDING',     # Spot → Funding Wallet
#         'FUNDING_MAIN',     # Funding Wallet → Spot
#         'MARGIN_FUNDING',   # Margin → Funding
#         'FUNDING_MARGIN',   # Funding → Margin
#     ]
#
#     headers = {
#         'X-MBX-APIKEY': api_key
#     }
#
#     print("\n=== История внутренних переводов ===")
#
#     found_any = False
#
#     for t_type in transfer_types:
#         params = {
#             'type': t_type,
#             'timestamp': int(time.time() * 1000),
#             # Опционально: раскомментируй, если нужно ограничить период
#             # 'startTime': int((time.time() - 30*24*60*60) * 1000),  # за 30 дней
#             # 'size': 50,
#         }
#         params['signature'] = sign_request(params, api_secret)
#
#         url = BASE_URL + '/sapi/v1/asset/transfer'
#         response = requests.get(url, headers=headers, params=params)
#
#         if response.status_code == 200:
#             data = response.json()
#             transfers = data.get('rows', [])
#             if transfers:
#                 found_any = True
#                 print(f"\n--- Переводы типа: {t_type} ---")
#                 for t in transfers:
#                     # print(
#                     #     f"Актив: {t['asset']} | Кол-во: {t['amount']} | "
#                     #     f"От: {t.get('fromAccountType', '-')} → К: {t.get('toAccountType', '-')} | "
#                     #     f"Дата: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(t['timestamp'] / 1000))}"
#                     # )
#                     from_acc, to_acc = get_transfer_direction(t_type)
#                     print(
#                         f"Актив: {t['asset']} | Кол-во: {t['amount']} | "
#                         f"От: {from_acc} → К: {to_acc} | "
#                         f"Дата: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(t['timestamp'] / 1000))}"
#                     )
#         else:
#             print(f"❌ Ошибка для типа {t_type}: {response.text}")
#     if not found_any:
#         print("Нет переводов ни по одному из типов.")
# # --- Запуск ---
# if __name__ == '__main__':
#     get_spot_balance()
#     print("\n" + "="*60 + "\n")
#     get_internal_transfers()

import datetime as dt
import hashlib
import hmac
import time
from urllib.parse import urlencode

import requests

from proxy import setup_proxy
from system.system import user, password, ip, port, api_key, api_secret

API_KEY = "ВАШ_API_KEY"
API_SECRET = "ВАШ_API_SECRET"
BASE = "https://api.binance.com"


def sign(params: dict, secret: str):
    qs = urlencode(params)
    signature = hmac.new(secret.encode(), qs.encode(), hashlib.sha256).hexdigest()
    return qs + "&signature=" + signature


def get_deposit_history(startTime=None, endTime=None, coin=None, limit=1000):
    setup_proxy(user=user, password=password, ip=ip, port=port)

    path = "/sapi/v1/capital/deposit/hisrec"
    ts = int(time.time() * 1000)
    params = {"timestamp": ts, "limit": limit}
    if startTime: params["startTime"] = int(startTime)
    if endTime: params["endTime"] = int(endTime)
    if coin: params["coin"] = coin

    signed_qs = sign(params, api_secret)
    headers = {"X-MBX-APIKEY": api_key}
    url = f"{BASE}{path}?{signed_qs}"
    r = requests.get(url, headers=headers, timeout=10)
    r.raise_for_status()
    return r.json()


if __name__ == "__main__":
    recs = get_deposit_history(limit=100)
    for r in recs:
        # ключевые поля: amount, coin, network, status, address, txId, insertTime
        # print(r)
        amount = float(r["amount"])
        symbol = r["coin"]
        to_address = r["address"]
        tx_id = r["txId"]
        time = dt.datetime.fromtimestamp(r["completeTime"] / 1000)

        print(f"{time} | {amount:>9.02f} {symbol} | на {to_address} | txid {tx_id}")
