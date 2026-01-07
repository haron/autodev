#!/usr/bin/env python3
import argparse
import sys

from decouple import config
from dotenv import load_dotenv
from telegram import Bot

load_dotenv()

TELEGRAM_BOT_TOKEN = config("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = config("TELEGRAM_CHAT_ID")


def main():
    if len(sys.argv) == 1:
        return

    has_dash_options = any(arg.startswith("-") for arg in sys.argv[1:])
    if has_dash_options:
        parser = argparse.ArgumentParser()
        parser.add_argument("--chat-id", help="Override chat ID")
        args, remaining = parser.parse_known_args()
        chat_id = args.chat_id or TELEGRAM_CHAT_ID
        message = " ".join(remaining) if remaining else ""
    else:
        chat_id = TELEGRAM_CHAT_ID
        message = " ".join(sys.argv[1:])

    if message:
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        bot.send_message(chat_id=chat_id, text=message)


if __name__ == "__main__":
    main()
