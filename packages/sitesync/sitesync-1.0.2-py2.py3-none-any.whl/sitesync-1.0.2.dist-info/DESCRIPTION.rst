sitesync
========

Script to sync db and/or data from remote host

Installation
------------

::

    pip install git+https://github.com/morlandi/sitesync


Usage
-----

Provides an easy way to build a working local copy from a remote site, either by:

1) DUMP: saving a copy of remote database and data into ./dump/HOST folder
2) SYNC: replacing local database and data downloading a fresh copy from remote host

Supported platforms:

1) Django (postgresql db + ./public/media/)
2) Workpress (mysql + ./www/wordpress/)


Usage: sitesync [-h] [-v {0,1,2,3}] [--dry-run] [--quiet] [--localhost]
                action target

Dump remote db and/or data, or Sync local db and/or data from remote instance

positional arguments:
  action                choices: sync, dump
  target                choices: db, data, all

optional arguments:
  -h, --help            show this help message and exit
  -v {0,1,2,3}, --verbosity {0,1,2,3}
                        Verbosity level. (default: 2)
  --dry-run, -d         simulate actions
  --quiet, -q           do not require user confirmation before executing commands
  --localhost, -l       dump db and data from localhost into ./dumps/localhost





History
=======

v1.0.2
------
* Python 2 & 3 compatibility

v1.0.1
------
* Few fixes for Python3

v1.0.0
------
* Initial setup


