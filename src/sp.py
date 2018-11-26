#!/usr/bin/env python3

# Copyright (C) 2018 Gary Blackwood <gary@garyblackwood.co.uk>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys
import signal
import logging
import atexit
import textwrap
import argparse
import requests
import colorama
import webbrowser
import pyperclip
from lxml import html

try:
    import readline  # Enables the use of hotkeys at the prompt e.g. ctrl+a.
except ImportError:
    pass  # Unavailable on Windows.


_VERSION_ = '1.0.0.dev1'

LOGGER = logging.getLogger(__name__)

PROMPT = 'sp (? for help)'

FAREWELL_MSG = 'Goodbye!'

DESCRIPTION = 'Search Startpage.com from the terminal.'

INFO_MSG = f"""
Version {_VERSION_}
Copyright © 2018 Gary Blackwood <gary@garyblackwood.co.uk>
License: GPLv3
Website: https://github.com/garee/sp
"""

PROMPT_HELP_MSG = """
1..10   open search result in web browser
c 1..10 copy the search result link to the clipboard
?       show help
q       exit
"""


@atexit.register
def on_exit():
    print(FAREWELL_MSG)


def configure_logging():
    fmt = '%(asctime)s - %(levelname)s - %(message)s'
    logging.basicConfig(format=fmt)


def init_debug_logging():
    LOGGER.setLevel(logging.DEBUG)
    LOGGER.debug('Version %s', _VERSION_)
    LOGGER.debug('Python version %s', get_python_version())


def configure_sigint_handler():
    def _sigint_handler(_signum, _frame):
        sys.exit(1)
    try:
        signal.signal(signal.SIGINT, _sigint_handler)
    except ValueError as ex:
        LOGGER.debug(ex)  # Only works on the main thread.


def get_python_version():
    return '%d.%d.%d' % sys.version_info[:3]


def search(query):
    url = 'https://www.startpage.com/do/search'
    data = {
        'cmd': 'process_search',
        'query': query
    }
    try:
        res = requests.post(url, data)
        return parse_search_result_page(res.content)
    except Exception as ex:
        LOGGER.error(ex)


def print_results(results):
    indent = ' ' * 4
    wrapper = textwrap.TextWrapper(width=80,
                                   initial_indent=indent,
                                   subsequent_indent=indent)
    fmt = wrapper.fill
    print()
    for i, result in enumerate(results):
        idx = (str(i+1) + '.').ljust(3)  # 'dd.'
        title = result['title']
        link = result['link']
        description = result['description']
        print(colorama.Fore.CYAN + idx, end=' ')
        print(colorama.Fore.MAGENTA + title)
        print(fmt(colorama.Fore.BLUE + link))
        if description:
            print(fmt(colorama.Fore.WHITE + description))
        print()


def parse_search_result_page(page):
    results = []
    tree = html.fromstring(page)
    result_nodes = tree.find_class('search-result')
    for node in result_nodes:
        title_nodes = node.find_class('search-item__title')
        subtitle_nodes = node.find_class('search-item__sub-title')
        description_nodes = node.find_class('search-item__body')
        title = title_nodes[0].xpath('a')[0].text_content()
        subtitle = subtitle_nodes[0].xpath('span')[0].text_content()
        description = description_nodes[0].text_content()
        results.append({
            'title': title,
            'link': subtitle,
            'description': description
        })
    return results


def get_prompt():
    color = colorama.Back.MAGENTA + colorama.Fore.BLACK
    color_reset = colorama.Back.RESET + colorama.Fore.RESET
    return color + PROMPT + color_reset + ' '


class SpREPL():
    def __init__(self, args):
        self.args = args
        self.prompt = get_prompt()
        self.results = []

    def once(self, cmd):
        self._handle_cmd(cmd)

    def loop(self):
        while True:
            cmd = self._read_command()
            self._handle_cmd(cmd)

    def _read_command(self):
        while True:
            try:
                cmd = input(self.prompt)
            except EOFError:
                sys.exit(0)
            cmd = ' '.join(cmd.split())
            if cmd:
                return cmd

    def _handle_cmd(self, cmd):
        if not cmd:
            return
        if cmd == '?':
            SpArgumentParser.print_prompt_help()
        elif cmd == 'q':
            sys.exit(0)
        elif cmd[0] == 'c' and len(cmd.split()) > 1:
            sub_cmds = cmd.split()
            if sub_cmds[1].isdigit():
                idx = int(sub_cmds[1])
                if idx >= 1 and idx <= len(self.results):
                    result = self.results[idx-1]
                    link = result['link']
                    pyperclip.copy(link)
                    print(f'Copied link: {link}')
                else:
                    print('Invalid search result index.')
            else:
                print('Invalid search result index.')
        elif cmd.isdigit():
            idx = int(cmd)
            if idx >= 1 and idx <= len(self.results):
                result = self.results[idx-1]
                webbrowser.open_new_tab(result['link'])
        else:
            query = '+'.join(cmd.split())
            self.results = search(query)
            print_results(self.results)


class SpArgumentParser(argparse.ArgumentParser):
    @staticmethod
    def print_prompt_help(file=None):
        file = sys.stderr if file is None else file
        file.write(textwrap.dedent(PROMPT_HELP_MSG))

    @staticmethod
    def print_info(file=None):
        file = sys.stderr if file is None else file
        file.write(textwrap.dedent(INFO_MSG))

    def print_help(self, file=None):
        super().print_help(file)
        self.print_info()


def parse_args():
    parser = SpArgumentParser(description=DESCRIPTION)
    parser.add_argument('keywords',
                        nargs='*',
                        help='search keywords')
    parser.add_argument('-d', '--debug',
                        action='store_true',
                        help='enable debug logging')
    parser.add_argument('-v', '--version',
                        action='version',
                        version=_VERSION_)
    return parser.parse_args()


def init():
    configure_logging()
    configure_sigint_handler()
    colorama.init()


def init_from_args(args):
    if args.debug:
        init_debug_logging()
        LOGGER.debug('Arguments: %s', ' '.join(sys.argv[1:]))


def start_repl(args):
    try:
        repl = SpREPL(args)
        if args.keywords:
            cmd = ' '.join(args.keywords)
            repl.once(cmd)
        else:
            repl.loop()
    except Exception as ex:
        LOGGER.error(ex)
        if LOGGER.isEnabledFor(logging.DEBUG):
            raise
        else:
            sys.exit(1)


def main():
    init()
    args = parse_args()
    init_from_args(args)
    start_repl(args)


if __name__ == '__main__':
    main()
