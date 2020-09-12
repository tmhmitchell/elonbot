import datetime as dt
import os
import re

import requests
import telegram.ext as ext

BOOT_TIME = dt.datetime.now(tz=dt.timezone.utc)
BOT_TOKEN = os.environ.get('ELONBOT_TG_TOKEN')
FINNHUB_TOKEN = os.environ.get('ELONBOT_FH_TOKEN')


def get_current_price(symbol):
    res = requests.get(
        'https://finnhub.io/api/v1/quote',
        params={
            'symbol': symbol,
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

    if any(regex.search(update.message.text) for regex in regexes):
        price = get_current_price('TSLA')
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f'TSLA @ ${price}'
        )

def stonks_command_handler(update, context):
    if BOOT_TIME > update.message.date:
        return
    
    if len(context.args) != 1:
        return

    # First argument to command is a stock symbol
    price = get_current_price(context.args[0].upper())
    update.message.reply_text(f'${price}')

if __name__ == '__main__':
    updater = ext.Updater(
        token=BOT_TOKEN, 
        use_context=True
    )
    dispatcher = updater.dispatcher

    dispatcher.add_handler(
        ext.MessageHandler(
            ext.Filters.text & (~ext.Filters.command),
            tsla_price_handler
        )
    )
    dispatcher.add_handler(ext.CommandHandler('stonks', stonks_command_handler))

    updater.start_polling()
