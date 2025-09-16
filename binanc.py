# -*- coding: utf-8 -*-
from binance import Client

from system.system import api_secret
from system.system import api_key

api_key = api_key
secret_key = api_secret

client = Client(api_key=api_key, api_secret=secret_key)
account = client.get_account()

for bal in account["balances"]:
    if float(bal['free']) > 0.0:
        print(f"{bal['asset'].ljust(10, '-')} {float(bal['free']):.3f}")
