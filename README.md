<h1 align="center">sp</h1>

<p align="center">
<a href="https://pypi.python.org/pypi/spcli"><img src="https://img.shields.io/pypi/v/spcli.svg?maxAge=600" alt="PyPI" /></a>
<a href="https://pypi.python.org/pypi/spcli"><img src="https://img.shields.io/pypi/pyversions/spcli.svg" alt="Python versions"></a>
<a href="https://github.com/garee/sp/blob/master/LICENSE"><img src="https://img.shields.io/github/license/garee/sp.svg" alt="License" /></a> <a href="https://travis-ci.org/Garee/sp"><img src="https://travis-ci.org/Garee/sp.svg?branch=master" alt="Build status"></a>
</p>

<p align="center">
<a href="https://asciinema.org/a/215549"><img src="https://asciinema.org/a/215549.png" alt="Asciicast" width="700"/></a>
</p>

`sp` is a command line utility to search Startpage.com from the terminal.

It is  inspired by the projects [ddgr](https://github.com/jarun/ddgr) and [googler](https://github.com/jarun/googler).



## Table of contents

- [Installation](#installation)
- [Usage](#usage)
  - [Command Line](#command-line)
  - [Interactive Mode](#interactive-mode)
- [Examples](#examples)
- [Browser Support](#browser-support)
- [Proxies](#proxies)
- [Development Quick Start](#development-quick-start)
- [Troubleshooting](#troubleshooting)

## Installation

```sh
$ pip install spcli
```

## Usage

### Command Line

```
$ sp -h
usage: sp.py [-h] [-d] [-f] [-s SITE] [-t SPAN] [-u] [-v] [-np]
             [--browser BROWSER] [--json] [--no-color]
             [keywords [keywords ...]]

Search Startpage.com from the terminal.

positional arguments:
  keywords              search keywords

optional arguments:
  -h, --help            show this help message and exit
  -d, --debug           enable debug logging
  -f, --first           open the first result in a web browser
  -s SITE, --site SITE  search a site
  -t SPAN, --time SPAN  time limit search to 1 d|w|m|y (day,week,month,year)
  -u, --unsafe          disable the family filter
  -v, --version         show program's version number and exit
  -np, --no-prompt      do not enter interactive mode
  --browser BROWSER     open results using this web browser
  --json                output the results in JSON; implies --no-prompt
  --no-color            disable color output

Version 1.0.1
Copyright © 2018 Gary Blackwood <gary@garyblackwood.co.uk>
License: GPLv3
Website: https://github.com/garee/sp
```

### Interactive Mode

```
f          view the first set of results
n          view the next set of results
p          view the previous set of results
[index]      open search result in web browser
c [index]    copy the search result link to the clipboard
s KEYWORDS perform a search for KEYWORDS
?          show help
q          exit
*          all other inputs are treated as new search keywords
```

## Examples

1. Search for terms.
```
$ sp hello world
```

2. Search `bbc.co.uk` for news about brexit:
```
$ sp -s bbc.co.uk brexit
```

3. Search for results from the past 24 hours.
```
$ sp -t d barcelona fc
```

4. Open the first result automatically
```
$ sp -f python docs
```

5. Disable safe search.
```
$ sp -u pawn
```

6. Output in JSON format.
```
$ sp --json climate change papers
```

## Browser Support

If the `BROWSER` environment variable exists, it will be used to open search results. If not, `sp` will attempt to use one from the [this list](https://docs.python.org/2/library/webbrowser.html#webbrowser.register).

You can specify which browser to use using the `--browser` flag. This also accepts a path to the browser executable.

```sh
$ sp --browser firefox
```
## Proxies

The requests library is used to perform the HTTP requests. You can configure proxies by [setting the environment variables](http://docs.python-requests.org/en/master/user/advanced/#proxies) `HTTP_PROXY` and `HTTPS_PROXY`.

```sh
$ export HTTP_PROXY="http://10.10.1.10:3128"
$ export HTTPS_PROXY="http://10.10.2.10.1080"
```

## Development Quick Start

Create and activate a virtual environment.
```sh
$ mkvirtualenv -p python3 sp
$ workon sp
```

Install the dependencies.

```sh
$ pip install -r requirements.txt
```

Format the code.

```sh
$ black sp/*.py
```

Run static analysis on the code.

```sh
$ pylint sp/*.py
$ flake8 sp/*.py
```

## Troubleshooting

Please [create an issue](https://github.com/Garee/sp/issues) for any problems that you encounter.

1. Disable the coloured output if it does not work correctly on your system:

```
$ sp --no-color
```