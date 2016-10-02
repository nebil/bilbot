#! usr/bin/env python

"""
Bilbot's magnificent engine.

Copyright (c) 2016, Nebil Kawas García
This source code is subject to the terms of the Mozilla Public License.
You can obtain a copy of the MPL at <https://www.mozilla.org/MPL/2.0/>.
"""

__AUTHOR__ = 'Nebil Kawas García'
__LICENSE__ = 'MPL-2.0'
__VERSION__ = '0.1.1'

import inspect
import logging
import os

from telegram.ext import CommandHandler, Updater
from telegram.update import Update

Update.reply = lambda self, message, **kwargs: \
    self.message.reply_text(message, **kwargs)


# USEFUL FUNCTIONS
# ====== =========

def _select_filename(basename):
    def get_fullpath(filename):
        current_dirname = os.path.dirname(os.path.realpath(__file__))
        return os.path.join(current_dirname, filename)

    local_filename = 'local-{}'.format(basename)
    basepath, local_filepath = map(get_fullpath, [basename, local_filename])

    return local_filepath if os.path.isfile(local_filepath) else basepath


def _get_commands():
    keep_name = lambda key: key.split('_')[0]  # from "help_command" to "help".
    return {keep_name(key): function
            for (key, function)
            in globals().items()
            if key.endswith('_command')}


def _to_money(amount):
    amount = int(amount)
    # REVIEW: should I use 'locale' configuration?
    return '{:,}'.format(amount).replace(',', '.')


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
    def process(line):
        name, amount = line.rstrip().split(FIELD_DELIMITER)
        update.reply("{} sacó ${}.".format(name, amount))
        return int(amount.replace('.', ''))

    try:
        with open(ACCOUNTS, 'r') as accounts:
            update.reply("Espera un poco, haré memoria de los hechos.")
            total = sum(process(line) for line in accounts)

            update.reply("Eso es todo lo que recuerdo.")
            update.reply("Por cierto, esto suma un gran total de...")
            update.reply("*{}* pesos chilenos.".format(_to_money(total)),
                         parse_mode='markdown')
    except FileNotFoundError:
        update.reply("No hay registros disponibles.")


def withdraw_command(bot, update, args):
    if len(args) == 0:
        update.reply("Debes agregar el monto, terrícola.")
    elif len(args) == 1:
        amount = _to_money(args[0])
        first_name = update.message.from_user.first_name
        message = ("¿Estás seguro de que deseas retirar *{}* pesos "
                   "del quiosco, {}?")
        update.reply(message.format(amount, first_name))

        with open(ACCOUNTS, 'a') as accounts:
            record = "{}{}{}\n".format(first_name, FIELD_DELIMITER, amount)
            accounts.write(record)

        update.reply("En realidad, da lo mismo: ya hice la operación.")
    else:
        update.reply("No te entiendo, humano.")


# SETTINGS
# ========

LOG_DIR = os.getenv('OPENSHIFT_LOG_DIR', '.')
LOGFILE = os.path.join(LOG_DIR, 'bilbot.log')
DATA_DIR = os.getenv('OPENSHIFT_DATA_DIR', '.')
ACCOUNTS = os.path.join(DATA_DIR, 'accounts.txt')

FIELD_DELIMITER = ';'
CONFIG_FILENAME = 'bilbot.cfg'
SELECTED_CONFIG = _select_filename(CONFIG_FILENAME)

with open(SELECTED_CONFIG) as cfgfile:
    CONFIG_DICT = dict(line.rstrip().split('=') for line in cfgfile)
    TGBOT_TOKEN = CONFIG_DICT.get('bot_token')

    if not TGBOT_TOKEN:
        raise Exception("\nThe bot token is missing."
                        "\nDeclare the token in the configuration file.")


if __name__ == '__main__':
    LOGFORMAT = ("\n{asctime}\n"
                 "====== ========\n"
                 "({levelname}) {message}\n")

    logging.basicConfig(level=logging.INFO,
                        filename=LOGFILE,
                        format=LOGFORMAT,
                        datefmt='%d/%b %H:%M:%S',
                        style='{')  # for enabling str.format()-style.

    updater = Updater(token=TGBOT_TOKEN)
    for name, callback in _get_commands().items():
        has_args = 'args' in inspect.signature(callback).parameters
        command_handler = CommandHandler(name, callback, pass_args=has_args)
        updater.dispatcher.add_handler(command_handler)

    updater.start_polling()
    updater.idle()
