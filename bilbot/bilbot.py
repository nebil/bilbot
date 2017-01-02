"""
Bilbot's magnificent engine.

Copyright (c) 2016-2017, Nebil Kawas García
This source code is subject to the terms of the Mozilla Public License.
You can obtain a copy of the MPL at <https://www.mozilla.org/MPL/2.0/>.
"""

__AUTHOR__ = 'Nebil Kawas García'
__LICENSE__ = 'MPL-2.0'
__VERSION__ = '0.3.0'

import inspect
import logging

import commands
import settings

from telegram.ext import (CommandHandler,
                          MessageHandler,
                          Filters,
                          Updater,
                          Dispatcher)


# MONKEY-PATCHING
# ===============

def _add_handlers(self):
    # first, add all the defined commands.
    all_commands = commands.COMMANDS.items()
    for name, callback in all_commands:
        has_args = 'args' in inspect.signature(callback).parameters
        command_handler = CommandHandler(name, callback, pass_args=has_args)
        self.add_handler(command_handler)

    # and then, handle the _faulty_ cases.
    unknown_handler = MessageHandler(Filters.command, commands.unknown)
    self.add_handler(unknown_handler)
Dispatcher.add_handlers = _add_handlers


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        filename=settings.LOGFILE,
                        format=settings.LOGFORMAT,
                        datefmt='%d/%b %H:%M:%S',
                        style='{')  # for enabling str.format()-style.

    updater = Updater(token=settings.BOT_TOKEN)
    updater.dispatcher.add_handlers()
    updater.start_polling()
    updater.idle()
