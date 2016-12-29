"""
This module stores Bilbot's changelog.

Copyright (c) 2016, Nebil Kawas García
This source code is subject to the terms of the Mozilla Public License.
You can obtain a copy of the MPL at <https://www.mozilla.org/MPL/2.0/>.
"""

from textwrap import dedent

INTRO = "This new {release_type} release comes up with the following changes,"

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
    {introduction}
    🚀 some minor code adjustments to deploy `bilbot` on OpenShift;
    📁 a new folder structure to offer an easier configuration;
    📢 a (very) simple logger to save information about errors;
    🎨 a little refactor to get a cleaner code.
    """),
    ########
    '0.1.2': dedent("""
    {introduction}
    🐛 a fix to several file-related edge-cases;
    🆕 a new handler to manage unknown commands;
    🎨 a small refactor to get a more extensible code.
    """),
    ########
    '0.1.3': dedent("""
    {introduction}
    🐛 a solution to handle `/list` with an empty file;
    💅 an improvement when dealing with unknown commands;
    📢 more logging information to know which commands were called;
    🎨 a good amount of refactoring attempts to get a simpler code.
    """),
    ########
    '0.1.4': dedent("""
    {introduction}
    💡 a revamp on Bilbot's replies to decrease their verbosity;
    🎨 some small-scale improvements to get a more legible code.
    """),
    ########
    '0.2.0': dedent("""
    {introduction}
    🔪 two cutting-edge commands: `rollback` and `clear`;
    📄 a new _changelog_ section for unveiling these life-changing updates;
    💁 a more informative `/help`, providing a description to each command;
    📚 a plethora of _docstrings_ and an opportune code restructuring;
    🐍 two observant cold-blooded linters: `pylint` and `flake8`;
    ⬆️ and, finally, an updated dependency.
    """),
    ########
    '0.2.1': dedent("""
    {introduction}
    🔒 a whitelist to prevent calling Bilbot from unauthorized chats;
    💥 a slight change to the saving format to avoid name collisions.
    """),
    ########
    '0.2.2': dedent("""
    {introduction}
    👮 a new condition before withdrawing to forbid far-fetched amounts;
    💅 some aesthetic refinements to the output of a couple of commands;
    🎨 a few refactoring efforts to get a more readable code.
    """),
}


def get_release_type(version):
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


def _fill_changelog(version):
    """
    Return a particular release changelog,
    filled in with its pertinent preamble.
    """

    type_ = get_release_type(version)
    intro = INTRO.format(release_type=type_)
    return RELEASES[version].format(introduction=intro)

RELEASES = {version: _fill_changelog(version) for version in RELEASES}
