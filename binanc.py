# -*- coding: utf-8 -*-
from binance import Client

from proxy import setup_proxy
from system.system import api_secret, api_key


def parse_binance():
    setup_proxy()

    client = Client(api_key=api_key, api_secret=api_secret)
    account = client.get_account()

    for bal in account["balances"]:
        if float(bal['free']) > 0.0:
            print(f"{bal['asset'].ljust(10, '-')} {float(bal['free']):.3f}")


if __name__ == '__main__':
    parse_binance()
