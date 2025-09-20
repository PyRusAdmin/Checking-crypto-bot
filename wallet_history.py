import json
from datetime import datetime, timezone, timedelta

from binance.client import Client
from binance.exceptions import BinanceAPIException
from dotenv import load_dotenv

from system.system import api_key, api_secret

# Загружаем .env
load_dotenv()

# API_KEY = os.getenv('BINANCE_API_KEY')
# API_SECRET = os.getenv('BINANCE_API_SECRET')
# api_key, api_secret


if not api_key or not api_secret:
    raise ValueError("API ключи не найдены в .env файле!")

client = Client(api_key, api_secret)


def get_wallet_history(asset='USDT', days=30):
    """
    Получает полную историю операций по указанному активу (по умолчанию USDT)
    за последние N дней.
    """
    # Рассчитываем timestamp начала периода
    end_time = int(datetime.now(timezone.utc).timestamp() * 1000)
    start_time = int((datetime.now(timezone.utc) - timedelta(days=days)).timestamp() * 1000)

    all_transactions = []

    print(f"🔍 Получаем историю кошелька для {asset} за последние {days} дней...\n")

    # 1. Депозиты (пополнения)
    try:
        deposits = client.get_deposit_history(coin=asset, startTime=start_time, endTime=end_time)
        for dep in deposits:
            all_transactions.append({
                "type": "deposit",
                "amount": float(dep['amount']),
                "status": dep['status'],
                "address": dep.get('address', '-'),
                "txId": dep.get('txId', '-'),
                "insertTime": datetime.fromtimestamp(dep['insertTime'] // 1000, tz=timezone.utc).strftime(
                    '%Y-%m-%d %H:%M:%S'),
                "network": dep.get('network', 'N/A')
            })
        print(f"📥 Депозитов найдено: {len(deposits)}")
    except BinanceAPIException as e:
        print(f"⚠️ Ошибка при получении депозитов: {e}")

    # 2. Выводы (withdrawals)
    try:
        withdrawals = client.get_withdraw_history(coin=asset, startTime=start_time, endTime=end_time)
        for wd in withdrawals:
            apply_time_raw = wd['applyTime']
            apply_time_formatted = "N/A"

            if isinstance(apply_time_raw, int) or (isinstance(apply_time_raw, str) and apply_time_raw.isdigit()):
                # Это timestamp в миллисекундах (например, "1712345678901")
                timestamp = int(apply_time_raw) // 1000
                apply_time_formatted = datetime.fromtimestamp(timestamp, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
            elif isinstance(apply_time_raw, str):
                try:
                    # Пытаемся распарсить как дату, например "2025-09-19 11:05:36"
                    dt = datetime.strptime(apply_time_raw, '%Y-%m-%d %H:%M:%S')
                    # Предположим, что время в UTC (если не указано иное)
                    dt = dt.replace(tzinfo=timezone.utc)
                    apply_time_formatted = dt.strftime('%Y-%m-%d %H:%M:%S')
                except ValueError:
                    # Не удалось распарсить — оставляем как есть или ставим заглушку
                    apply_time_formatted = apply_time_raw

            all_transactions.append({
                "type": "withdrawal",
                "amount": float(wd['amount']),
                "status": wd['status'],
                "address": wd.get('address', '-'),
                "txId": wd.get('txId', '-'),
                "applyTime": apply_time_formatted,
                "network": wd.get('network', 'N/A'),
                "transactionFee": float(wd.get('transactionFee', 0))
            })
        print(f"📤 Выводов найдено: {len(withdrawals)}")
    except BinanceAPIException as e:
        print(f"⚠️ Ошибка при получении выводов: {e}")

    # 3. Спотовые сделки, где участвовал USDT (опционально)
    try:
        # Получим все символы, где есть USDT
        exchange_info = client.get_exchange_info()
        usdt_symbols = [s['symbol'] for s in exchange_info['symbols'] if 'USDT' in s['symbol']]

        trades_total = 0
        for symbol in usdt_symbols[:10]:  # Ограничим первыми 10 парами для скорости (можно убрать)
            trades = client.get_my_trades(symbol=symbol, startTime=start_time, endTime=end_time, limit=1000)
            for trade in trades:
                # Определяем, была ли это покупка или продажа
                is_buyer = trade['isBuyer']
                quote_asset = symbol.replace(trade['symbol'].replace('USDT', ''),
                                             '')  # грубое определение — лучше парсить через exchange_info
                if 'USDT' in quote_asset:
                    # USDT — квотируемая валюта (например, BTCUSDT), значит, amount — это BTC, а сумма в USDT = qty * price
                    usdt_amount = float(trade['qty']) * float(trade['price'])
                    direction = "BUY" if is_buyer else "SELL"
                else:
                    # USDT — базовая валюта (маловероятно, но на всякий случай)
                    usdt_amount = float(trade['quoteQty'])
                    direction = "SELL" if is_buyer else "BUY"  # логика может отличаться

                all_transactions.append({
                    "type": f"spot_trade_{direction}",
                    "symbol": trade['symbol'],
                    "usdt_amount": round(usdt_amount, 2),
                    "price": float(trade['price']),
                    "qty": float(trade['qty']),
                    "time": datetime.fromtimestamp(trade['time'] // 1000, tz=timezone.utc).strftime(
                        '%Y-%m-%d %H:%M:%S'),
                    "orderId": trade['orderId']
                })
            trades_total += len(trades)
        print(f"💱 Спотовых сделок с USDT найдено: {trades_total}")
    except BinanceAPIException as e:
        print(f"⚠️ Ошибка при получении спотовых сделок: {e}")

    # Сортируем по времени
    all_transactions.sort(key=lambda x: x.get('insertTime') or x.get('applyTime') or x.get('time'))

    print(f"\n✅ Всего операций найдено: {len(all_transactions)}\n")
    print(json.dumps(all_transactions, indent=4, ensure_ascii=False))

    # Экспорт в файл
    filename = f"wallet_history_{asset}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(all_transactions, f, indent=4, ensure_ascii=False)
    print(f"💾 Сохранено в файл: {filename}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Получить историю кошелька USDT на Binance')
    parser.add_argument('--asset', type=str, default='USDT', help='Актив, например USDT, BTC')
    parser.add_argument('--days', type=int, default=30, help='Количество дней назад для поиска истории')
    args = parser.parse_args()

    get_wallet_history(asset=args.asset, days=args.days)
