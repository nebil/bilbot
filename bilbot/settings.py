"""
This module stores Bilbot's configuration.

Copyright (c) 2016-2017, Nebil Kawas García
This source code is subject to the terms of the Mozilla Public License.
You can obtain a copy of the MPL at <https://www.mozilla.org/MPL/2.0/>.
"""

import os
from collections import namedtuple


# USEFUL FUNCTIONS
# ====== =========

def _is_useful(line):
    """
    Check whether a line is empty or is a comment.

    >>> _is_useful('                          \n')
    False

    >>> _is_useful(' # This line shall be false!')
    False
    """

    is_empty = not line.lstrip()
    is_comment = line.lstrip().startswith('#')

    return not (is_empty or is_comment)


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


# EXCEPTIONS
# ==========

MISSING_BOT_TOKEN = ("\nThe bot token is missing."
                     "\nPlease, declare the token in the configuration file.")

NONPOSITIVE_VALUE = ("\n{amount} is not a valid configuration value."
                     "\nPlease, declare a positive {m__}imal amount.")

MIN_GT_MAX_VALUES = ("\nThe minimum value ({min:,}) cannot be greater than "
                     "\nthe maximum value ({max:,})."
                     "\nPlease, adjust these values.")


# SETTINGS
# ========

LOG_DIR = os.getenv('OPENSHIFT_LOG_DIR', '.')
LOGFILE = os.path.join(LOG_DIR, 'bilbot.log')
DATA_DIR = os.getenv('OPENSHIFT_DATA_DIR', '.')
ACCOUNTS = os.path.join(DATA_DIR, 'accounts.txt')

FIELD_DELIMITER = ';'
GROUP_DELIMITER = '='
CONFIG_FILENAME = 'bilbot.cfg'
SELECTED_CONFIG = _select_filename(CONFIG_FILENAME)

CSV_KWARGS = {
    'delimiter': FIELD_DELIMITER,
    'lineterminator': '\n',
}

LOGFORMAT = ("\n{asctime}\n"
             "====== ========\n"
             "({levelname}) {message}\n")


with open(SELECTED_CONFIG) as cfgfile:
    CONFIG_DICT = dict(line.rstrip().split('=')
                       for line in cfgfile
                       if _is_useful(line))

    BOT_TOKEN = CONFIG_DICT.get('bot_token')
    WHITELIST = CONFIG_DICT.get('whitelist')
    MIN_AMOUNT = int(CONFIG_DICT.get('min_withdrawal') or 500)
    MAX_AMOUNT = int(CONFIG_DICT.get('max_withdrawal') or 100000)

    # pylint: disable=invalid-name
    error = namedtuple('error', ['message', 'kwargs'])

    EXCEPTIONS = {
        not BOT_TOKEN:
        error(MISSING_BOT_TOKEN, {}),

        MIN_AMOUNT < 1:
        error(NONPOSITIVE_VALUE, {'amount': MIN_AMOUNT, 'm__': 'min'}),

        MAX_AMOUNT < 1:
        error(NONPOSITIVE_VALUE, {'amount': MAX_AMOUNT, 'm__': 'max'}),

        MIN_AMOUNT > MAX_AMOUNT:
        error(MIN_GT_MAX_VALUES, {'min': MIN_AMOUNT, 'max': MAX_AMOUNT}),
    }

    for check, error in EXCEPTIONS.items():
        if check: raise Exception(error.message.format(**error.kwargs))
