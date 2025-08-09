from os import getenv

from aiogram import Bot, Dispatcher, html

# Bot token can be obtained via https://t.me/BotFather
TOKEN = getenv("BOT_TOKEN")

# All handlers should be attached to the Router (or Dispatcher)

dp = Dispatcher()


def main():
    print("Hello from crypto-bot!")


if __name__ == "__main__":
    main()
