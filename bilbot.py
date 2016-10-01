"""
Bilbot's magnificent engine.

Copyright (c) 2016, Nebil Kawas García
This source code is subject to the terms of the Mozilla Public License.
You can obtain a copy of the MPL at <https://www.mozilla.org/MPL/2.0/>.
"""

from telegram.ext import CommandHandler, Updater


def start_command(bot, update):
    update.message.reply_text("Bilbot, operativo.")

with open('bilbot.cfg') as cfgfile:
    CONFIG_DICT = dict(line.rstrip().split('=') for line in cfgfile)
    TGBOT_TOKEN = CONFIG_DICT.get('bot_token')

    if not TGBOT_TOKEN:
        raise Exception("\nThe bot token is missing."
                        "\nDeclare the token in the configuration file.")

updater = Updater(token=TGBOT_TOKEN)
updater.dispatcher.add_handler(CommandHandler('start', start_command))
updater.start_polling()
updater.idle()
