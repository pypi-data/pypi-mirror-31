submitty-config
===============
[![Build Status](https://travis-ci.org/Submitty/submitty-config.svg?branch=master)](https://travis-ci.org/Submitty/submitty-config)
[![PyPI Version](https://img.shields.io/pypi/v/submitty-config.svg)](https://pypi.org/project/submitty-config/)
![Python Versions](https://img.shields.io/pypi/pyversions/submitty-config.svg)

submitty-config provides CLI tool to help interact with [Submitty](http://submitty.org) and 
[configuring its autograder](http://submitty.org/instructor/assignment_configuration).

Installation
------------
Use [pip](https://pypi.org/) to install [submitty-config](https://pypi.org/project/submitty-config/):
```
pip install submitty-config
```

From source:
```
git clone https://github.com/Submitty/submitty-config
cd submitty-config
python3 setup.py install
```

Usage
-----
```
$ submitty-config --help                                                                                                                                             [21:30:26]
usage: submitty-config [-h] [--version] command ...

positional arguments:
    lint      lint a config file

optional arguments:
  -h, --help  show this help message and exit
  --version   show program's version number and exit
```

Linting a file:
```
submitty-config lint <path_to_file>
```
