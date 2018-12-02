<h1 align="center">sp</h1>

`sp` is a command line utility to search Startpage.com from the terminal.

It is  inspired by the projects [ddgr](https://github.com/jarun/ddgr) and [googler](https://github.com/jarun/googler).

<a href="https://github.com/garee/sp/blob/master/LICENSE"><img src="https://img.shields.io/github/license/garee/sp.svg" alt="License" /></a> <a href="https://travis-ci.org/Garee/sp"><img src="https://travis-ci.org/Garee/sp.svg?branch=master" alt="Build status"></a>

## Command Line Usage

```
$ sp -h
usage: sp.py [-h] [-t SPAN] [-s SITE] [--no-color] [-d] [-v]
             [keywords [keywords ...]]

Search Startpage.com from the terminal.

positional arguments:
  keywords       search keywords

optional arguments:
  -h, --help            show this help message and exit
  -t SPAN, --time SPAN  time limit search to 1 d|w|m|y (day,week,month,year)
  -s SITE, --site SITE  search a site
  --no-color            disable color output
  -d, --debug           enable debug logging
  -v, --version         show program's version number and exit

Version 1.0.0.dev1
Copyright © 2018 Gary Blackwood <gary@garyblackwood.co.uk>
License: GPLv3
Website: https://github.com/garee/sp
```

## Interactive Mode Usage

```
n       view the next set of results
p       view the previous set of results
1..10   open search result in web browser
c 1..10 copy the search result link to the clipboard
?       show help
q       exit
*       all other inputs are treated as new search keywords
```

## Examples

Display the first ten search results for the keyword 'Python':
```
$ sp Python

1.  Welcome to Python.org
    https://www.python.org/
    The official home of the Python Programming Language.

...
```

Search `bbc.co.uk` for news about brexit:
```
$ sp -s bbc.co.uk brexit

1.  Brexit: All you need to know about the UK leaving the EU - BBC News
    https://www.bbc.co.uk/news/uk-politics-32810887
    Here is an easy-to-understand guide to Brexit - beginning with the
    basics, then a look at the current negotiations, followed by a selection of
    answers to questions ...

...
```

Search for football results from the past 24 hours:
```
$ sp -t d Football

1.  Watch: Liverpool loanee Harry Wilson scores ... - Planet Football
    https://www.planetfootball.com/videos/watch-liverpool-loanee-harry-
    wilson-scores-screamer-for-derby/
    Planet Football; 1st December 2018. Harry Wilson has been making a name
    for himself on loan at Derby from Liverpool this season – and on Saturday he
    added  ...

...
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
$ black src/*.py
```

Run static analysis on the code.

```sh
$ pylint src/*.py
$ flake8 src/*.py
```

Generate a distribution package in `./dist`.

```sh
$ python setup.py sdist bdist_wheel
```
