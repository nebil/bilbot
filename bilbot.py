#! usr/bin/env python

"""
Bilbot's magnificent engine.

Copyright (c) 2016, Nebil Kawas García
This source code is subject to the terms of the Mozilla Public License.
You can obtain a copy of the MPL at <https://www.mozilla.org/MPL/2.0/>.
"""

__AUTHOR__ = 'Nebil Kawas García'
__LICENSE__ = 'MPL-2.0'
__VERSION__ = '0.1.4'

import inspect
import logging
import os

from argparse import Namespace
from functools import wraps
from textwrap import dedent

from telegram.ext import (CommandHandler,
                          MessageHandler,
                          Filters,
                          Updater,
                          Dispatcher)
from telegram.update import Update


# MONKEY-PATCHING
# ===============

def _add_handlers(self):
    # first, add all the defined commands.
    for name, callback in _get_commands().items():
        has_args = 'args' in inspect.signature(callback).parameters
        command_handler = CommandHandler(name, callback, pass_args=has_args)
        self.add_handler(command_handler)

    # and then, handle the _faulty_ cases.
    unknown_handler = MessageHandler([Filters.command], unknown)
    self.add_handler(unknown_handler)
Dispatcher.add_handlers = _add_handlers


def _reply(self, message):
    # using a 'LBYL' approach.

    # if hasattr(self, 'buffer'):
    #     self.buffer.append(message)
    # else:
    #     self.buffer = [message]

    # using a 'EAFP' approach.

    # try:
    #     self.buffer.append(message)
    # except AttributeError:
    #     self.buffer = [message]

    # finally, using a smoother approach. :-)

    self.buffer = getattr(self, 'buffer', [])
    self.buffer.append(message)
Update.reply = _reply


def _send(self, **kwargs):
    sent_message = '\n'.join(self.buffer)
    self.message.reply_text(sent_message, **kwargs)
Update.send = _send


# USEFUL FUNCTIONS
# ====== =========

def logger(command):
    @wraps(command)
    def wrapper(bot, update, **kwargs):
        command(     update, **kwargs)
        message = LOG_TEMPLATE.format(user=update.message.from_user.first_name,
                                      command=command.__name__)
        logging.info(message)
    return wrapper


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
    # REVIEW: should I use 'locale' configuration?
    return '{:,}'.format(amount).replace(',', '.')


# COMMANDS
# ========

@logger
def start_command(update):
    update.reply(INFO.START)
    update.send()


@logger
def about_command(update):
    update.reply(INFO.ABOUT.format(version=__VERSION__))
    update.send(parse_mode='markdown')


@logger
def help_command(update):
    command_list = map(CMD_TEMPLATE.format, sorted(_get_commands()))
    help_message = HELP_MESSAGE.format(commands=', '.join(command_list))
    update.reply(help_message)
    update.send(parse_mode='markdown')


@logger
def list_command(update):
    def is_not_empty(filepath):
        return os.path.isfile(filepath) and os.path.getsize(filepath)

    def process(line):
        name, amount = line.rstrip().split(FIELD_DELIMITER)
        update.reply(INFO.EACH_LIST.format(user=name, amount=amount))
        return int(amount.replace('.', ''))

    if is_not_empty(ACCOUNTS):
        with open(ACCOUNTS, 'r') as accounts:
            update.reply(INFO.ANTE_LIST)
            total = sum(process(line) for line in accounts)
            update.reply(INFO.POST_LIST.format(amount=_to_money(total)))
    else:
        update.reply(ERROR.NO_STORED_ACCOUNTS)
    update.send(parse_mode='markdown')


@logger
def withdraw_command(update, args):
    def add_record(name, amount):
        with open(ACCOUNTS, 'a') as accounts:
            record = REC_TEMPLATE.format(user=name,
                                         delimiter=FIELD_DELIMITER,
                                         amount=amount)
            accounts.write(record)

    def withdraw(amount):
        if amount < 1:
            update.reply(ERROR.NONPOSITIVE_AMOUNT)
        else:
            amount = _to_money(amount)
            first_name = update.message.from_user.first_name
            message = INFO.ANTE_WITHDRAW.format(amount=amount, user=first_name)
            update.reply(message)
            add_record(first_name, amount)
            update.reply(INFO.POST_WITHDRAW)

    if len(args) == 0:
        update.reply(ERROR.MISSING_AMOUNT)
    elif len(args) == 1:
        try:
            amount = int(args[0])
        except ValueError:
            update.reply(ERROR.UNSOUND_AMOUNT)
        else:
            withdraw(amount)
    else:
        update.reply(ERROR.TOO_MANY_ARGUMENTS)
    update.send(parse_mode='markdown')


@logger
def clear_command(update):
    with open(ACCOUNTS, 'w'):
        pass

    # NOTE: I could also write...
    # open(ACCOUNTS, 'w').close()

    update.reply(INFO.POST_CLEAR)
    update.send()


def unknown(bot, update):
    unknown_command, *_ = update.message.text.split()
    update.reply(ERROR.UNKNOWN_COMMAND.format(command=unknown_command))
    update.send(parse_mode='markdown')


# EXCEPTIONS
# ==========

MISSING_TOKEN = ("\nThe bot token is missing."
                 "\nPlease, declare the token in the configuration file.")


# ERROR MESSAGES
# ===== ========

ERROR = Namespace(**{
    'MISSING_AMOUNT':     "Debes agregar el monto, terrícola.",
    'UNSOUND_AMOUNT':     "El monto es inválido.",
    'TOO_MANY_ARGUMENTS': "No te entiendo, humano.",
    'NONPOSITIVE_AMOUNT': "El argumento debe ser estrictamente positivo.",
    'NO_STORED_ACCOUNTS': "No hay registros disponibles.",

    'UNKNOWN_COMMAND': dedent("""
                       El comando `{command}` no existe.
                       Escribe `/help` para obtener una lista de comandos.
                       """),
})


# INFO MESSAGES
# ==== ========

INFO = Namespace(**{
    'START': "Bilbot, operativo.",
    'ABOUT': dedent("""
             Hola, mi nombre es Nebilbot.
             Pero también me puedes llamar Bilbot.
             Mi versión es `{version}`.
             """),

    # from Latin: 'ante' --> before,
    #             'post' --> after.
    'POST_CLEAR': "Todo listo: he eliminado cualquier rastro de registros.",

    'ANTE_WITHDRAW': "¿Estás seguro de que deseas retirar *{amount}* pesos "
                     "del quiosco, {user}?",
    'POST_WITHDRAW': "En realidad, da lo mismo: ya hice la operación.",

    'ANTE_LIST': "Espera un poco, haré memoria de los hechos.",
    'EACH_LIST': "{user} sacó ${amount}.",
    'POST_LIST': dedent("""
                 Eso es todo lo que recuerdo.
                 Por cierto, esto suma un gran total de...
                 *{amount}* pesos chilenos.
                 """),
})


# TEMPLATES
# =========

CMD_TEMPLATE = "`/{}`"
LOG_TEMPLATE = "{user} called {command}."
REC_TEMPLATE = "{user}{delimiter}{amount}\n"
HELP_MESSAGE = "Mis comandos son: {commands}."


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
        raise Exception(MISSING_TOKEN)


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
    updater.dispatcher.add_handlers()
    updater.start_polling()
    updater.idle()
