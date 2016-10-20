"""
This module stores Bilbot's changelog.

Copyright (c) 2016, Nebil Kawas García
This source code is subject to the terms of the Mozilla Public License.
You can obtain a copy of the MPL at <https://www.mozilla.org/MPL/2.0/>.
"""

from textwrap import dedent

RELEASES = {
    '0.1.0': dedent("""
    This first release comes up with an initial backbone for building `bilbot`.
    It provides five embryonic commands:
    `about`, `help`, `list`, `start`, `withdraw`.

    Additionally, it also includes,
    📚 a `README.md` file with (not very) useful information;
    📜 a prolix file with the [MPL v2.0](https://www.mozilla.org/MPL/2.0);
    🤖 a [dummy file](pseudo-bilbot.cfg) to adjust settings;
    🔧 a short and sweet `.gitignore` file;
    🐍 and, finally, a briefer `requirements.txt` file.
    """),
    ########
    '0.1.1': dedent("""
    This new patch release comes up with the following changes,
    🚀 some minor code adjustments to deploy `bilbot` on OpenShift;
    📁 a new folder structure to offer an easier configuration;
    📢 a (very) simple logger to save information about errors;
    🎨 a little refactor to get a cleaner code.
    """),
    ########
    '0.1.2': dedent("""
    This new patch release comes up with the following changes,
    🐛 a fix to several file-related edge-cases;
    🆕 a new handler to manage unknown commands;
    🎨 a small refactor to get a more extensible code.
    """),
    ########
    '0.1.3': dedent("""
    This new patch release comes up with the following changes,
    🐛 a solution to handle `/list` with an empty file;
    💅 an improvement when dealing with unknown commands;
    📢 more logging information to know which commands were called;
    🎨 a good amount of refactoring attempts to get a simpler code.
    """),
    ########
    '0.1.4': dedent("""
    This new patch release comes up with the following changes,
    💡 a revamp on Bilbot's replies to decrease their verbosity;
    🎨 some small-scale improvements to get a more legible code.
    """),
}
