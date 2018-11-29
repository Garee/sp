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
import webbrowser
import requests
import colorama
import pyperclip
from lxml import html

try:
    import readline  # Enables the use of hotkeys at the prompt e.g. ctrl+a.
except ImportError:
    pass  # Unavailable on Windows.

_VERSION_ = "1.0.0.dev1"

LOGGER = logging.getLogger(__name__)

MSG = {
    "prompt": "sp (? for help)",
    "farewell": "Goodbye!",
    "description": "Search Startpage.com from the terminal.",
    "info": f"""
Version {_VERSION_}
Copyright © 2018 Gary Blackwood <gary@garyblackwood.co.uk>
License: GPLv3
Website: https://github.com/garee/sp""",
    "help": """    n       view the next set of results
    p       view the previous set of results
    1..10   open search result in web browser
    c 1..10 copy the search result link to the clipboard
    ?       show help
    q       exit
    *       all other inputs are treated as new search keywords
    """,
    "invalid_idx": "Invalid search result index.",
}


class SpREPL:
    def __init__(self, args):
        self.args = args
        self.prompt = self._get_prompt()
        self.query = None
        self.results = []
        self.page = None
        self.actions = [
            {"match": lambda cmd: cmd is None, "action": lambda cmd: None},
            {"match": "?", "action": lambda cmd: SpArgumentParser.print_prompt_help()},
            {"match": "n", "action": self._on_matches_next},
            {"match": "p", "action": self._on_matches_prev},
            {"match": self._matches_copy_link, "action": self._on_matches_copy_link},
            {
                "match": lambda cmd: cmd.isdigit(),
                "action": self._on_matches_open_result,
            },
            {"match": "q", "action": lambda cmd: sys.exit(0)},
        ]
        self.searcher = SpSearcher()

    def start(self, before_loop=lambda: None):
        if self.args.keywords:
            self.once()
        else:
            before_loop()
            self.loop()

    def once(self):
        cmd = " ".join(self.args.keywords)
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
            cmd = " ".join(cmd.split())
            if cmd:
                return cmd

    def _handle_cmd(self, cmd):
        def matches(cmd, action):
            if callable(action["match"]):
                return action["match"](cmd)
            return cmd == action["match"]

        action_filter = filter(lambda a: matches(cmd, a), self.actions)
        action = next(action_filter, {"action": self._search})
        action["action"](cmd)

    def _on_matches_next(self, _cmd=None):
        if self.page is not None:
            self.page += 1
            self.results = self.searcher.search(self.query, page=self.page)
            self.print_results(self.results, start_idx=self.page * 10)

    def _on_matches_prev(self, _cmd=None):
        if self.page and self.page > 0:
            self.page -= 1
            self.results = self.searcher.search(self.query, page=self.page)
            self.print_results(self.results, start_idx=self.page * 10)

    def _matches_copy_link(self, cmd):
        return cmd[0] == "c" and len(cmd.split()) > 1

    def _on_matches_copy_link(self, cmd):
        sub_cmds = cmd.split()
        first_cmd = sub_cmds[1]
        if first_cmd.isdigit():
            idx = int(first_cmd)
            if 0 < idx <= len(self.results):
                result = self.results[idx - 1]
                link = result["link"]
                pyperclip.copy(link)
                print(f"Copied link: {link}")
            else:
                print(MSG["invalid_index"])
        else:
            print(MSG["invalid_index"])

    def _on_matches_open_result(self, cmd):
        idx = int(cmd)
        if 0 < idx <= len(self.results):
            result = self.results[idx - 1]
            webbrowser.open_new_tab(result["link"])
        else:
            print(MSG["invalid_index"])

    def _search(self, cmd):
        self.page = 0
        self.query = "+".join(cmd.split())
        self.results = self.searcher.search(self.query)
        self.print_results(self.results)

    def print_results(self, results, start_idx=0):
        print()
        for i, result in enumerate(results):
            idx = (str(start_idx + i + 1) + ".").ljust(3)  # 'dd.'
            self._print_idx(idx)
            self._print_title(result["title"])
            self._print_link(result["link"])
            if result["description"]:
                self._print_description(result["description"])
            print()

    def _print_idx(self, idx):
        color = colorama.Fore.CYAN
        if self.args.noColor:
            color = colorama.Style.RESET_ALL
        print(color + idx, end=" ")

    def _print_title(self, title):
        color = colorama.Fore.MAGENTA
        if self.args.noColor:
            color = colorama.Style.RESET_ALL
        print(color + title)

    def _print_link(self, link):
        color = colorama.Fore.BLUE
        if self.args.noColor:
            color = colorama.Style.RESET_ALL
        print(self._fmt_text(color + link))

    def _print_description(self, desc):
        color = colorama.Style.RESET_ALL
        print(self._fmt_text(color + desc))

    def _fmt_text(self, text):
        indent = " " * 4
        wrapper = textwrap.TextWrapper(
            width=80, initial_indent=indent, subsequent_indent=indent
        )
        return wrapper.fill(text)

    def _get_prompt(self):
        color = colorama.Back.MAGENTA + colorama.Fore.BLACK
        reset = colorama.Style.RESET_ALL
        if self.args.noColor:
            color = colorama.Style.RESET_ALL
        return color + MSG["prompt"] + reset + " "


class SpSearcher:
    search_url = "https://www.startpage.com/do/search"

    def __init__(self):
        self.page_size = 10
        self.qid = ""

    def search(self, query, page=0):
        data = {
            "cmd": "process_search",
            "query": query,
            "startat": page * self.page_size,
            "rcount": int(page / 2),
            "qid": self.qid,
            "abp": -1,
            "cat": "web",
            "engine0": "v1all",
            "language": "english",
            "rl": "NONE",
            "t": "default",
        }
        try:
            res = requests.post(self.search_url, data)
            self.qid = self._parse_qid(res.content)
            return self.parse_search_result_page(res.content)
        except Exception as ex:
            LOGGER.error(ex)

    def parse_search_result_page(self, page):
        results = []
        tree = html.fromstring(page)
        result_nodes = tree.find_class("search-result")
        for node in result_nodes:
            title_nodes = node.find_class("search-item__title")
            subtitle_nodes = node.find_class("search-item__sub-title")
            description_nodes = node.find_class("search-item__body")
            title = title_nodes[0].xpath("a")[0].text_content()
            subtitle = subtitle_nodes[0].xpath("span")[0].text_content()
            description = description_nodes[0].text_content()
            results.append(
                {"title": title, "link": subtitle, "description": description}
            )
        return results

    def _parse_qid(self, page):
        tree = html.fromstring(page)
        for form in tree.forms:
            for inp in form.inputs:
                if inp.name == "qid":
                    return inp.value
        return ""


class SpArgumentParser(argparse.ArgumentParser):
    def __init__(self):
        super().__init__(description=MSG["description"])
        self.add_argument("keywords", nargs="*", help="search keywords")
        self.add_argument(
            "--no-color",
            action="store_true",
            dest="noColor",
            help="disable color output",
        )
        self.add_argument(
            "-d", "--debug", action="store_true", help="enable debug logging"
        )
        self.add_argument("-v", "--version", action="version", version=_VERSION_)

    @staticmethod
    def print_prompt_help(file=None):
        file = sys.stderr if file is None else file
        file.write(textwrap.dedent(MSG["help"]))

    @staticmethod
    def print_info(file=None):
        file = sys.stderr if file is None else file
        file.write(textwrap.dedent(MSG["info"]))

    def print_help(self, file=None):
        super().print_help(file)
        self.print_info()


def configure_logging():
    fmt = "%(asctime)s - %(levelname)s - %(message)s"
    logging.basicConfig(format=fmt)


def init_debug_logging():
    LOGGER.setLevel(logging.DEBUG)
    LOGGER.debug("Version %s", _VERSION_)
    LOGGER.debug("Python version %d.%d.%d", *sys.version_info[:3])


def configure_sigint_handler():
    def _sigint_handler(_signum, _frame):
        sys.exit(1)

    try:
        signal.signal(signal.SIGINT, _sigint_handler)
    except ValueError as ex:
        LOGGER.debug(ex)  # Only works on the main thread.


def configure_exit_msg():
    atexit.register(lambda: print(MSG["farewell"]))


def init():
    configure_logging()
    configure_sigint_handler()


def init_from_args(args):
    if args.debug:
        init_debug_logging()
        LOGGER.debug("Arguments: %s", " ".join(sys.argv[1:]))
    if not args.noColor:
        colorama.init(autoreset=True)
    if args.keywords:
        try:
            readline.add_history(" ".join(args.keywords))
        except Exception:
            pass  # Unavailable on Windows.


def start_repl(args):
    try:
        repl = SpREPL(args)
        repl.start(before_loop=configure_exit_msg)
    except Exception as ex:
        LOGGER.error(ex)
        if LOGGER.isEnabledFor(logging.DEBUG):
            raise
        else:
            sys.exit(1)


def main():
    init()
    args = SpArgumentParser().parse_args()
    init_from_args(args)
    start_repl(args)


if __name__ == "__main__":
    main()
