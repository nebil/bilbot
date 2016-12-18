#! usr/bin/env python

"""
Bilbot's magnificent engine.

Copyright (c) 2016, Nebil Kawas García
This source code is subject to the terms of the Mozilla Public License.
You can obtain a copy of the MPL at <https://www.mozilla.org/MPL/2.0/>.
"""

__AUTHOR__ = 'Nebil Kawas García'
__LICENSE__ = 'MPL-2.0'
__VERSION__ = '0.2.2'

import inspect
import logging
import os

from functools import wraps
from subprocess import check_output
import changelog
from messages import ERROR, INFO

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
    for name, callback in COMMANDS.items():
        has_args = 'args' in inspect.signature(callback).parameters
        command_handler = CommandHandler(name, callback, pass_args=has_args)
        self.add_handler(command_handler)

    # and then, handle the _faulty_ cases.
    unknown_handler = MessageHandler(Filters.command, unknown)
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


def _select_filename(basename):
    """
    Return the absolute path of a particular file,
    taking into account if a local version exists.

    # If the local file doesn't exist:
    >>> _select_filename('bilbot.cfg')
    '/absolute/path/bilbot.cfg'

    # Otherwise, it would return...
    >>> _select_filename('bilbot.cfg')
    '/absolute/path/local-bilbot.cfg'
    """

    def get_fullpath(filename):
        """
        Provide the absolute path to a particular file,
        considering the current location of the script.

        >>> get_fullpath('bilbot.cfg')
        'absolute/path/to/bilbot.cfg'
        """

        current_dirname = os.path.dirname(os.path.realpath(__file__))
        return os.path.join(current_dirname, filename)

    local_filename = 'local-{}'.format(basename)
    basepath, local_filepath = map(get_fullpath, [basename, local_filename])

    return local_filepath if os.path.isfile(local_filepath) else basepath


def _get_last_line():
    last_line = check_output(['tail', '-1', ACCOUNTS]).decode('utf-8')
    return last_line.rstrip().split(FIELD_DELIMITER)


def _get_last_ppid():
    return _get_last_line()[0]


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


def _get_release_type(version):
    """
    Indicate whether is a major, minor or patch release.

    >>> get_release_type('3.1.4')
    'patch'

    >>> get_release_type('4.2.0')
    'minor'

    >>> get_release_type('5.0.0')
    'major'
    """

    # NOTE: I think this is an elegant implementation.
    major, minor, patch = map(int, version.split('.'))
    if patch: return 'patch'
    if minor: return 'minor'
    if major: return 'major'


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
    """

    update.reply(INFO.START)
    update.send()


@logger
@sentry
def about_command(update, args):
    """
    Conoce algo sobre mí.
    """

    def format_(version):
        release_type = _get_release_type(version)
        return VER_TEMPLATE[release_type].format(version)

    if len(args) == 0:
        update.reply(INFO.ABOUT.format(version=__VERSION__))
    elif len(args) == 1:
        argument = args[0]
        if argument == 'releases':
            numbers = map(format_, sorted(changelog.RELEASES.keys()))
            message = INFO.ABOUT_RELEASES.format(releases=_itemize(numbers))
        else:
            error_message = ERROR.WRONG_ARGUMENT.format(argument=argument)
            message = changelog.RELEASES.get(argument, error_message)
        update.reply(message)
    else:
        update.reply(ERROR.TOO_MANY_ARGUMENTS)
    update.send(parse_mode='markdown')


@logger
@sentry
def help_command(update):
    """
    Recibe (un poco de) ayuda.
    """

    def format_(name, function, length):
        docstring = inspect.getdoc(function)
        return CMD_TEMPLATE.format(command=name,
                                   description=docstring,
                                   fill=length)

    cmd_dict = sorted(COMMANDS.items())
    max_length = max(map(len, COMMANDS))  # find the longest command.
    commands = (format_(*cmd, length=max_length) for cmd in cmd_dict)
    help_message = INFO.HELP.format(commands=_itemize(commands))
    update.reply(help_message)
    update.send(parse_mode='markdown')


@logger
@sentry
def new_command(update):
    """
    Inicia un nuevo periodo.
    """

    last_ppid, *rest = _get_last_line()
    is_already_opened = _is_not_empty(ACCOUNTS) and not any(rest)
    if is_already_opened:
        update.reply(ERROR.ALREADY_OPENED)
    else:
        with open(ACCOUNTS, 'a') as accounts:
            new_ppid = int(last_ppid or 0) + 1
            boundary = NEW_TEMPLATE.format(ppid=new_ppid,
                                           delimiter=FIELD_DELIMITER)
            accounts.write(boundary)
        update.reply(INFO.POST_NEW.format(user=update.user.first_name))
    update.send()


@logger
@sentry
def list_command(update):
    """
    Muestra todos los registros.
    """

    def is_from_ppid(line, ppid):
        line_ppid, *rest = line.rstrip().split(FIELD_DELIMITER)
        return line_ppid == ppid if any(rest) else None

    def process(line):
        """
        Process a string with a "<uuid>;<name>;<amount>" format,
        replying to the user and returning the amount.

        >>> process('314225;Alice;7.650\n')
        7650          # (a message is sent)
        """

        *_, name, amount = line.rstrip().split(FIELD_DELIMITER)
        update.reply(INFO.EACH_LIST.format(user=name, amount=amount))
        return int(amount.replace('.', ''))

    last_ppid, *rest = _get_last_line()
    if _is_not_empty(ACCOUNTS) and any(rest):
        with open(ACCOUNTS, 'r') as accounts:
            update.reply(INFO.ANTE_LIST)
            total = sum(process(line) for line in accounts
                        if is_from_ppid(line, last_ppid))
            update.reply(INFO.POST_LIST.format(amount=_to_money(total)))
    else:
        update.reply(ERROR.NO_STORED_ACCOUNTS)
    update.send(parse_mode='markdown')


@logger
@sentry
def withdraw_command(update, args):
    """
    Agrega un nuevo registro.
    """

    def add_record(ppid, uuid, name, amount):
        """
        Write a new record into the accounts document,
        using the following format: "<uuid>;<name>;<amount>".

        >>> add_record(314225, 'Alice', '650')
        write('314225;Alice;650\n')

        >>> add_record(631104, 'Bob', '4.200')
        write('631104;Bob;4.200\n')
        """

        with open(ACCOUNTS, 'a') as accounts:
            record = REC_TEMPLATE.format(ppid=ppid,
                                         uuid=uuid,
                                         user=name,
                                         amount=amount,
                                         delimiter=FIELD_DELIMITER)
            accounts.write(record)

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


# EXCEPTIONS
# ==========

MISSING_TOKEN = ("\nThe bot token is missing."
                 "\nPlease, declare the token in the configuration file.")


# TEMPLATES
# =========

CMD_TEMPLATE = "`{command:>{fill}}` — {description}"
LOG_TEMPLATE = "{user} called {command}."
NEW_TEMPLATE = "{ppid}{delimiter}\n"
REC_TEMPLATE = "{ppid}{delimiter}{uuid}{delimiter}{user}{delimiter}{amount}\n"
VER_TEMPLATE = {
    'major': '✨ `{}`',
    'minor': '🎁 `{}`',
    'patch': '📦 `{}`'
}


# SETTINGS
# ========

LOG_DIR = os.getenv('OPENSHIFT_LOG_DIR', '.')
LOGFILE = os.path.join(LOG_DIR, 'bilbot.log')
DATA_DIR = os.getenv('OPENSHIFT_DATA_DIR', '.')
ACCOUNTS = os.path.join(DATA_DIR, 'accounts.txt')

MIN_AMOUNT = 500
MAX_AMOUNT = 100000

FIELD_DELIMITER = ';'
CONFIG_FILENAME = 'bilbot.cfg'
SELECTED_CONFIG = _select_filename(CONFIG_FILENAME)

with open(SELECTED_CONFIG) as cfgfile:
    CONFIG_DICT = dict(line.rstrip().split('=') for line in cfgfile)
    BOT_TOKEN = CONFIG_DICT.get('bot_token')
    WHITELIST = CONFIG_DICT.get('whitelist')

    if not BOT_TOKEN:
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

    COMMANDS = _get_commands()
    updater = Updater(token=BOT_TOKEN)
    updater.dispatcher.add_handlers()
    updater.start_polling()
    updater.idle()
