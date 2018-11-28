<h1 align="center">sp</h1>

`sp` is a command line utility to search Startpage.com from the terminal.

It is  inspired by the projects [ddgr](https://github.com/jarun/ddgr) and [googler](https://github.com/jarun/googler).

<a href="https://github.com/garee/sp/blob/master/LICENSE"><img src="https://img.shields.io/github/license/garee/sp.svg" alt="License" /></a>

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

Run static analysis on the code.

```sh
$ pylint src/*.py
$ flake8 src/*.py
```

Generate a distribution package in `./dist`.

```sh
$ python setup.py sdist bdist_wheel
```
