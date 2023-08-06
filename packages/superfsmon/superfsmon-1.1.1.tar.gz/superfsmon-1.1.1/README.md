# Superfsmon

Supervisor plugin to watch a directory and restart programs on changes

## Overview

Superfsmon is especially useful during development to restart applications
when the code changes. It can monitor a directory for changes, filter the
file paths by glob patterns or regular expressions and restart Supervisor
programs individually or by group.

Superfsmon uses Supervisor's XML-RPC API. Your
`supervisord.conf` file must have a valid `[unix_http_server]` or
`[inet_http_server]` section and a `[rpcinterface:supervisor]` section.
If you are able to control your Supervisor instance with `supervisorctl`, you
have already met these requirements.

To restart your celery workers on changes in the `/app/devops` directory your
`supervisord.conf` could look like this.

    [program:celery]
    command=celery -A devops.celery worker --loglevel=INFO --concurrency=10

    [program:superfsmon]
    command=superfsmon /app/devops celery

You can use multiple instances of Superfsmon to control different programs.

## Installation

### Python 2

    pip install superfsmon

### Python 3

This script requires Supervisor which [is not yet available for Python
3][Supervisor Python 3]. To be able to install superfsmon without errors you
need to install the development version of Supervisor from the GitHub
repository first. The development version may not work reliably, don't use it
in production.

    pip install git+https://github.com/Supervisor/supervisor
    pip install superfsmon

[Supervisor Python 3]: https://github.com/Supervisor/supervisor/issues/510

## Command Line Arguments

    usage: superfsmon [-h] [-e FLAG] [--disable [FLAG]] [-r PATTERN] [-i PATTERN]
                      [--recognize-regex REGEX] [--ignore-regex REGEX] [-f] [-c]
                      [-d] [--no-recursion] [-g GROUP] [-a]
                      PATH [PROG [PROG ...]]

    Supervisor plugin to watch a directory and restart programs on changes

    optional arguments:
      -h, --help            show this help message and exit
      -e FLAG, --enable FLAG
                            disable functionality if flag is not set
      --disable [FLAG]      disable functionality if flag is set

    directory monitoring:
      PATH                  directory path to watch for changes
      -r PATTERN, --recognize PATTERN
                            recognize changes to file paths matching the pattern
      -i PATTERN, --ignore PATTERN
                            ignore changes to file paths matching the pattern
      --recognize-regex REGEX
                            recognize changes to file paths matching the regular
                            expression
      --ignore-regex REGEX  ignore changes to file paths matching the regular
                            expression
      -f, --hidden-files    recognize changes to hidden files
      -c, --case-insensitive
                            case insensitive file path matching
      -d, --directories     recognize changes to directories
      --no-recursion        don't watch for changes in subdirectories

    programs:
      PROG                  supervisor program name to restart
      -g GROUP, --group GROUP
                            supervisor group name to restart
      -a, --any             restart any child of this supervisor

## Examples

Only recognize changes to `.py` files:

    command=superfsmon /app/devops celery -r *.py

Restart all Supervisor programs in the `workers` group:

    command=superfsmon /app/devops -g workers

Disable functionality using an environment variable (useful for production):

    command=superfsmon /app/devops celery -e %(CELERY_AUTORELOAD)s

## Known Issues

* The `--ignore` option is case insensitive. When using `--case-insensitive`
  it is case sensitive. This is caused by a [bug in Watchdog][Watchdog Issue].

[Watchdog Issue]: https://github.com/gorakhargosh/watchdog/issues/442

## License

Copyright (C) 2018 Tim Schumacher

License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>.

This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent per‐mitted by law.
