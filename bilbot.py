"""
Bilbot's magnificent engine.

Copyright (c) 2016, Nebil Kawas García
This source code is subject to the terms of the Mozilla Public License.
You can obtain a copy of the MPL at <https://www.mozilla.org/MPL/2.0/>.
"""

from telegram.ext import CommandHandler, Updater
from telegram.update import Update

Update.reply = lambda self, message, **kwargs: \
    self.message.reply_text(message, **kwargs)


def _get_commands():
    def keep_name(key):
        return key.split('_')[0]

    return {keep_name(key): function for (key, function) in globals().items()
            if key.endswith('_command')}


# COMMANDS
# ========

def start_command(bot, update):
    update.reply("Bilbot, operativo.")


def about_command(bot, update):
    update.reply("Hola, mi nombre es Nebilbot.")
    update.reply("Pero también me puedes llamar Bilbot.")


def help_command(bot, update):
    update.reply("Mis comandos son: `/about`, `/help`, `/list`, `/start`.",
                 parse_mode='markdown')


def list_command(bot, update):
    # REVIEW: should I use 'locale' configuration?
    to_money = lambda amount: '{:,}'.format(int(amount)).replace(',', '.')

    update.reply("Espera un poco, haré memoria de los hechos.")

    def process(line):
        name, amount = line.rstrip().split(';')
        update.reply("{} sacó ${}.".format(name, amount))
        return int(amount.replace('.', ''))

    with open('accounts.txt', 'r') as accounts:
        total = sum(process(line) for line in accounts)

    update.reply("Eso es todo lo que recuerdo.")
    update.reply("Por cierto, esto suma un gran total de...")
    update.reply("*{}* pesos chilenos.".format(to_money(total)),
                 parse_mode='markdown')

with open('bilbot.cfg') as cfgfile:
    CONFIG_DICT = dict(line.rstrip().split('=') for line in cfgfile)
    TGBOT_TOKEN = CONFIG_DICT.get('bot_token')

    if not TGBOT_TOKEN:
        raise Exception("\nThe bot token is missing."
                        "\nDeclare the token in the configuration file.")

updater = Updater(token=TGBOT_TOKEN)
for name, callback in _get_commands().items():
    updater.dispatcher.add_handler(CommandHandler(name, callback))

updater.start_polling()
updater.idle()
