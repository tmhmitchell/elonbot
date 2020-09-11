import datetime as dt
import os
import re

import requests
import telegram.ext as ext

BOOT_TIME = dt.datetime.now(tz=dt.timezone.utc)
BOT_TOKEN = os.environ.get('ELONBOT_TG_TOKEN')
FINNHUB_TOKEN = os.environ.get('ELONBOT_FH_TOKEN')

updater = ext.Updater(
    token=BOT_TOKEN, 
    use_context=True
)
dispatcher = updater.dispatcher


def get_current_tsla_price():
    res = requests.get(
        'https://finnhub.io/api/v1/quote',
        params={
            'symbol': 'TSLA',
            'token': FINNHUB_TOKEN 
        }
    )
    return res.json().get('c')


def tsla_price_handler(update, context):
    # Ignore any message that came through prior to the bot booting
    if BOOT_TIME > update.message.date:
        return

    regexes = [
        re.compile(pattern, re.IGNORECASE) 
        for pattern in ['.+lon', 'musk', 'te?sla', 'mars', 'sec']
    ]

    message_text = update.message.text

    if any(regex.search(message_text) for regex in regexes):
        price = get_current_tsla_price()
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f'TSLA @ ${price}'
        )

# Add all our command handlers
dispatcher.add_handler(
    ext.MessageHandler(
        ext.Filters.text & (~ext.Filters.command), 
        tsla_price_handler
    )
)

updater.start_polling()
