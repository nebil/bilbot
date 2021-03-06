"""
This module stores Bilbot's commands.

Copyright (c) 2016, Nebil Kawas García
This source code is subject to the terms of the Mozilla Public License.
You can obtain a copy of the MPL at <https://www.mozilla.org/MPL/2.0/>.
"""

import csv
import inspect
import logging
import os

from collections import defaultdict, namedtuple
from functools import reduce, wraps
from subprocess import check_output

from bilbot import __VERSION__
import changelog
from messages import ERROR, INFO
from settings import (WHITELIST,
                      ACCOUNTS,
                      FIELD_DELIMITER,
                      GROUP_DELIMITER,
                      CSV_KWARGS,
                      MIN_AMOUNT,
                      MAX_AMOUNT)

from telegram.update import Update


# MONKEY-PATCHING
# ===============

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
    sent_message = _itemize(self.buffer)
    self.message.reply_text(sent_message, **kwargs)
Update.send = _send

Update.user = property(lambda self: self.message.from_user)


# USEFUL FUNCTIONS
# ====== =========

# pylint: disable=no-member
# =======

def logger(command):
    """
    Add a logger to the decorated command.
    """

    @wraps(command)
    # pylint: disable=bad-whitespace
    # pylint: disable=unused-argument
    def wrapper(bot, update, **kwargs):
        command(     update, **kwargs)
        if command.__name__ == 'unknown':
            command.__name__ = _get_command_name(update.message.text)
        message = LOG_TEMPLATE.format(user=update.user.first_name,
                                      command=command.__name__)
        logging.info(message)
    return wrapper


def sentry(command):
    """
    Add a sentry to the decorated command.
    """

    @wraps(command)
    def wrapper(update, **kwargs):
        chat_id = str(update.message.chat.id)
        if WHITELIST is None or chat_id in WHITELIST.split(','):
            command(update, **kwargs)
        else:
            name = update.user.first_name
            update.reply(ERROR.NOT_AUTHORIZED.format(user=name))
            update.send()
    return wrapper


def _is_not_empty(filepath):
    """
    Check whether a file is empty or not.

    >>> _is_not_empty('empty.txt')
    False
    """

    return os.path.isfile(filepath) and os.path.getsize(filepath)


def _get_last_line():
    """
    Return the last line written in the accounts file.
    It could be a withdrawal or a new purchase period.

    >>> _get_last_line()
    ['2', 631104, 'Bob', '4.200']

    # a purchase period is opened
    >>> _get_last_line()
    ['3=', '']
    """

    last_line = check_output(['tail', '-1', ACCOUNTS]).decode('utf-8')
    return last_line.rstrip().split(FIELD_DELIMITER)


def _get_last_ppid():
    """
    Return the current 'ppid' as a string
    (aka. the purchase period identifier).

    >>> _get_last_ppid()
    '3'
    """

    last_ppid, *_ = _get_last_line()
    return last_ppid.replace(GROUP_DELIMITER, '')


def _get_commands():
    """
    Yield all the defined commands.

    >>> _get_commands()
    {'foo': <function foo_command at [...]>,
     'bar': <function bar_command at [...]>,
     'qux': <function qux_command at [...]>}
    """

    keep_name = lambda key: key.split('_')[0]  # from "help_command" to "help".
    return {keep_name(key): function
            for (key, function)
            in globals().items()
            if key.endswith('_command')}


def _get_command_name(text):
    """
    Extract the command name from a user input.

    >>> _get_command_name('/command arg1 arg2')
    '/command'
    """

    # pylint: disable=unused-variable
    command, *args = text.split()
    return command


def _itemize(iterable):
    """
    Return an itemized string from an iterable.

    >>> _itemize(['seis', 'siete', 'ocho'])
    'seis
    siete
    ocho'
    """

    return '\n'.join(iterable)


def _to_money(amount):
    """
    Return a formatted amount of money,
    using dots as thousands separators.

    >>> _to_money(123)
    '123'

    >>> _to_money(1234567890)
    '1.234.567.890'
    """

    # REVIEW: should I use 'locale' configuration?
    return '{:,}'.format(amount).replace(',', '.')


# COMMANDS
# ========

# NOTE: These decorators **must** be applied in the following order:
# ===== [1] @logger,
#       [2] @sentry.
#       Otherwise, the unauthorized requests will not be registered.
@logger
@sentry
def start_command(update):
    """
    Enciende a `nebilbot`.
    🚀 `start` 🚀

    Este comando sirve para finalizar mi somnolencia.
    Pero también puedes usarlo para saber si es que estoy encendido.
    Como podrás colegir, astuto terrícola, ahora sí estoy encendido.
    """

    update.reply(INFO.START)
    update.send()


@logger
@sentry
def about_command(update, args):
    """
    Conoce algo sobre mí.
    🔍 `about` 🔍

    Este comando entrega información relacionada a mí.
    • `/about` ofrece información básica acerca de mí;
    • `/about releases` devuelve mi extenso historial de versiones;
    • `/about <versión>` informa sobre ese _release_ en particular.
    Por ejemplo, para obtener el _changelog_ de la versión `0.2.2`:
    `/about 0.2.2`
    """

    def format_(version):
        release_type = changelog.get_release_type(version)
        return VER_TEMPLATE[release_type].format(version)

    if len(args) == 0:
        update.reply(INFO.ABOUT.format(version=__VERSION__))
    elif len(args) == 1:
        argument = args[0]
        releases = changelog.RELEASES
        if argument == 'releases':
            numbers = map(format_, sorted(releases.keys()))
            message = INFO.ABOUT_RELEASES.format(releases=_itemize(numbers))
        elif argument == 'latest':
            update.reply(INFO.ABOUT_LATEST.format(latest=__VERSION__))
            message = releases[__VERSION__]
        else:
            error_message = ERROR.WRONG_ARGUMENT.format(argument=argument)
            message = releases.get(argument, error_message)
        update.reply(message)
    else:
        update.reply(ERROR.TOO_MANY_ARGUMENTS)
    update.send(parse_mode='markdown')


@logger
@sentry
def help_command(update, args):
    """
    Recibe (un poco de) ayuda.
    ℹ️ `help` ℹ️

    Este comando cuenta con dos modalidades.
    • `/help` entrega un breve resumen de los comandos disponibles;
    • `/help <comando>` proporciona más detalles sobre ese comando.
    """

    def format_(name, function, length):
        summary, *_ = inspect.getdoc(function).split('\n')
        return CMD_TEMPLATE.format(command=name,
                                   summary=summary,
                                   fill=length)

    if len(args) == 0:
        cmd_dict = sorted(COMMANDS.items())
        max_length = max(map(len, COMMANDS))  # find the longest command.
        commands = (format_(*cmd, length=max_length) for cmd in cmd_dict)
        help_message = INFO.HELP.format(commands=_itemize(commands))
        update.reply(help_message)
    elif len(args) == 1:
        cmd_name = args[0]
        cmd_func = COMMANDS.get(cmd_name, None)
        if cmd_func:
            _, *details = inspect.getdoc(cmd_func).split('\n')
            update.reply(_itemize(details))
        else:
            cmd_name = '/{}'.format(cmd_name)
            update.reply(ERROR.UNKNOWN_COMMAND.format(command=cmd_name))
    else:
        update.reply(ERROR.TOO_MANY_ARGUMENTS)
    update.send(parse_mode='markdown')


@logger
@sentry
def new_command(update):
    """
    Inicia un nuevo periodo.
    🆕 `new` 🆕

    Este comando establece un nuevo periodo de compras.
    Cada transacción está enmarcada en un único periodo.
    Cada periodo puede almacenar una o más transacciones.
    """

    last_ppid, *rest = _get_last_line()
    is_already_opened = _is_not_empty(ACCOUNTS) and not any(rest)
    if is_already_opened:
        update.reply(ERROR.ALREADY_OPENED)
    else:
        with open(ACCOUNTS, 'a') as accounts:
            new_ppid = int(last_ppid or 0) + 1
            boundary = NEW_TEMPLATE.format(ppid=new_ppid,
                                           delimiter=GROUP_DELIMITER)
            accounts.write(boundary)
        update.reply(INFO.POST_NEW.format(user=update.user.first_name))
    update.send()


@logger
@sentry
def list_command(update, args):
    """
    Muestra todos los registros.
    📊 `list` 📊

    Este comando cuenta con dos modalidades.
    • `/list` muestra una lista con las transacciones realizadas;
    • `/list agg` añade, además, los datos agregados por usuario.
    """

    def is_from_ppid(line, ppid):
        """
        Check whether a withdrawal is from a specific period.

        >>> is_from_ppid('1;314;Alice;7.650\n', '1')
        True

        >>> is_from_ppid('2=\n', '2')
        False
        """

        line_ppid, *rest = line
        return line_ppid == ppid if any(rest) else None

    def process(line):
        """
        Process a string with a "<ppid>;<uuid>;<name>;<amount>" format,
        replying to the user and returning the amount.

        >>> process('1;314225;Alice;7.650\n')
        7650            # (a message is sent)
        """

        *_, uuid, name, amount = line
        update.reply(INFO.EACH_LIST.format(user=name, amount=amount))
        user = namedtuple('user', ['uuid', 'name'])
        return user(uuid, name), int(amount.replace('.', ''))

    def sum_amount(aggregate, row_record):
        """
        Add an amount of money to a specific user,
        to build a dictionary with aggregate data.

        >>> sum_amount({'Alice': 600, Bob': 500},
                                    ('Bob', 300))
        {'Alice': 600, 'Bob': 800}
        """

        user, amount = row_record
        aggregate[user] += amount
        return aggregate

    last_ppid, *rest = _get_last_line()
    if _is_not_empty(ACCOUNTS) and any(rest):
        with open(ACCOUNTS, 'r') as accounts:
            reader = csv.reader(accounts, **CSV_KWARGS)
            update.reply(INFO.ANTE_LIST)
            from_last_ppid = (process(line) for line in reader
                              if is_from_ppid(line, last_ppid))

            aggregate = reduce(sum_amount, from_last_ppid, defaultdict(int))
            total = sum(aggregate.values())
            update.reply(INFO.POST_LIST.format(amount=_to_money(total)))

            if args and args[0] == 'agg':
                update.reply(INFO.POST_AGGREGATE_LIST)
                for user, amount in aggregate.items():
                    amount = _to_money(amount)
                    update.reply(INFO.EACH_LIST.format(user=user.name,
                                                       amount=amount))
    else:
        update.reply(ERROR.NO_STORED_ACCOUNTS)
    update.send(parse_mode='markdown')


@logger
@sentry
def withdraw_command(update, args):
    """
    Agrega un nuevo registro.
    💸 `withdraw` 💸

    Este comando registra un nueva transacción.
    Por ejemplo, para almacenar tres mil pesos:
    `/withdraw 3000`
    """

    def add_record(ppid, uuid, name, amount):
        """
        Write a new record into the accounts document,
        using the following format: "<ppid>;<uuid>;<name>;<amount>".

        >>> add_record('1', 314225, 'Alice', '650')
        write('1;314225;Alice;650\n')

        >>> add_record('2', 631104, 'Bob', '4.200')
        write('2;631104;Bob;4.200\n')
        """

        with open(ACCOUNTS, 'a') as accounts:
            writer = csv.writer(accounts, **CSV_KWARGS)
            writer.writerow([ppid, uuid, name, amount])

    def withdraw(amount):
        """
        Withdraw a specific amount of money,
        informing the user about this transaction.

        >>> withdraw(200)
        # OK

        >>> withdraw('two hundred pesos')
        # ValueError
        """

        if MIN_AMOUNT <= amount <= MAX_AMOUNT:
            amount = _to_money(amount)
            ppid = _get_last_ppid()
            uuid = update.user.id
            first_name = update.user.first_name
            message = INFO.ANTE_WITHDRAW.format(amount=amount, user=first_name)
            update.reply(message)
            add_record(ppid, uuid, first_name, amount)
            update.reply(INFO.POST_WITHDRAW)
        elif amount < 1:
            update.reply(ERROR.NONPOSITIVE_AMOUNT)
        else:
            update.reply(ERROR.UNREALISTIC_AMOUNT)

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
@sentry
def rollback_command(update):
    """
    Borra el registro más nuevo.
    ⏪ `rollback` ⏪

    En términos generales, este comando revierte la operación más reciente.
    Por ejemplo, es posible borrar un _withdrawal_ con un monto incorrecto.
    🚫 No es posible hacer `rollback` de un `clear` o de un mismo `rollback`.
    """

    if _is_not_empty(ACCOUNTS):
        lines = open(ACCOUNTS, 'r').readlines()
        with open(ACCOUNTS, 'w') as accounts:
            accounts.writelines(lines[:-1])
        update.reply(INFO.POST_ROLLBACK)
    else:
        update.reply(ERROR.NO_STORED_ACCOUNTS)
    update.send()


@logger
@sentry
def clear_command(update):
    """
    Elimina todos los registros.
    🔥 `clear` 🔥

    Este comando suprime todos los registros almacenados.
    ⚠️ Esto puede provocar efectos altamente destructivos.
    """

    if _is_not_empty(ACCOUNTS):
        with open(ACCOUNTS, 'w'):
            pass

        # NOTE: I could also write...
        # open(ACCOUNTS, 'w').close()

        update.reply(INFO.POST_CLEAR)
    else:
        update.reply(ERROR.NO_STORED_ACCOUNTS)
    update.send()


@logger
@sentry
def unknown(update):
    """
    Handle (almost) all the nonexistent commands.
    """

    unknown_command = _get_command_name(update.message.text)
    update.reply(ERROR.UNKNOWN_COMMAND.format(command=unknown_command))
    update.send(parse_mode='markdown')


# TEMPLATES
# =========

CMD_TEMPLATE = "`{command:>{fill}}` — {summary}"
LOG_TEMPLATE = "{user} called {command}."
NEW_TEMPLATE = "{ppid}{delimiter}\n"
VER_TEMPLATE = {
    'major': '✨ `{}`',
    'minor': '🎁 `{}`',
    'patch': '📦 `{}`'
}

COMMANDS = _get_commands()
