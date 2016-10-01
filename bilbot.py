"""
Bilbot's magnificent engine.

Copyright (c) 2016, Nebil Kawas García
This source code is subject to the terms of the Mozilla Public License.
You can obtain a copy of the MPL at <https://www.mozilla.org/MPL/2.0/>.
"""

__AUTHOR__ = 'Nebil Kawas García'
__LICENSE__ = 'MPL-2.0'
__VERSION__ = '0.1.0'

import inspect

from telegram.ext import CommandHandler, Updater
from telegram.update import Update

Update.reply = lambda self, message, **kwargs: \
    self.message.reply_text(message, **kwargs)


# USEFUL FUNCTIONS
# ====== =========

def _get_commands():
    def keep_name(key):
        return key.split('_')[0]

    return {keep_name(key): function for (key, function) in globals().items()
            if key.endswith('_command')}

# REVIEW: should I use 'locale' configuration?
_to_money = lambda amount: '{:,}'.format(int(amount)).replace(',', '.')


# COMMANDS
# ========

def start_command(bot, update):
    update.reply("Bilbot, operativo.")


def about_command(bot, update):
    update.reply("Hola, mi nombre es Nebilbot.")
    update.reply("Pero también me puedes llamar Bilbot.")
    update.reply("Mi versión es `{}`.".format(__VERSION__),
                 parse_mode='markdown')


def help_command(bot, update):
    update.reply("Mis comandos son: "
                 "`/about`, `/help`, `/list`, `/start`, `/withdraw`.",
                 parse_mode='markdown')


def list_command(bot, update):
    update.reply("Espera un poco, haré memoria de los hechos.")

    def process(line):
        name, amount = line.rstrip().split(';')
        update.reply("{} sacó ${}.".format(name, amount))
        return int(amount.replace('.', ''))

    with open('accounts.txt', 'r') as accounts:
        total = sum(process(line) for line in accounts)

    update.reply("Eso es todo lo que recuerdo.")
    update.reply("Por cierto, esto suma un gran total de...")
    update.reply("*{}* pesos chilenos.".format(_to_money(total)),
                 parse_mode='markdown')


def withdraw_command(bot, update, args):
    amount = _to_money(args[0])
    first_name = update.message.from_user.first_name
    message = "¿Estás seguro de que deseas retirar *{}* pesos del quiosco, {}?"
    update.reply(message.format(amount, first_name))

    with open('accounts.txt', 'a') as accounts:
        record = "{};{}\n".format(first_name, amount)
        accounts.write(record)

    update.reply("En realidad, da lo mismo: ya hice la operación.")

with open('bilbot.cfg') as cfgfile:
    CONFIG_DICT = dict(line.rstrip().split('=') for line in cfgfile)
    TGBOT_TOKEN = CONFIG_DICT.get('bot_token')

    if not TGBOT_TOKEN:
        raise Exception("\nThe bot token is missing."
                        "\nDeclare the token in the configuration file.")

updater = Updater(token=TGBOT_TOKEN)
for name, callback in _get_commands().items():
    has_args = 'args' in inspect.signature(callback).parameters
    command_handler = CommandHandler(name, callback, pass_args=has_args)
    updater.dispatcher.add_handler(command_handler)

updater.start_polling()
updater.idle()
