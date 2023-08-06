fdump
==================================================
[![Build Status](https://travis-ci.org/nul-one/fdump.png)](https://travis-ci.org/nul-one/fdump)
[![PyPI version](https://badge.fury.io/py/fdump.svg)](https://badge.fury.io/py/fdump)
[![License](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)
[![Requirements Status](https://requires.io/github/nul-one/fdump/requirements.svg?branch=master)](https://requires.io/github/nul-one/fdump/requirements/?branch=master)

Split stdin by lines based on regex and output to stdout or dump to a file.

Installation
-------------------------

### install from pypi (recommend)
`pip3 install fdump`

### install from github (latest master)
`pip3 install -U git+https://github.com/nul-one/fdump.git`

Usage
-------------------------

```
Tool for spliting stream lines based on regular expression matching. Each line from STDIN
will be sent to dump file if it matches given regular expression and a dump file path is
specified or to STDOUT if it doesn't match. Lines will always be appended to the end of a
dump file. Multiple `-d` and `-g` options can be used, each receiving and processing  the
output of previous one.

Usage:
   fdump [OPTIONS]

Options:
    -d REGEX [DUMPFILE] -   Lines from STDIN or previous -d/-g that match REGEX will be
                            dumped to DUMPFILE file or /dev/null if used without DUMPFILE.
                            The rest goes to the next -d/-g or if this is the last one, to
                            STDOUT.

    -g REGEX [DUMPFILE] -   Same as -d but inverted: matching regexes are printed or passed
                            and non matching are dumped to DUMPFILE or /dev/null.

    -p REGEX [OUTPUT]   -   Lines from STDIN or previous -d/-g will be parsed using regex
                            and the output will be comma separated regex groups, or if
                            OUTPUT is defined, it will substitute '{{N}}' strings in OUTPUT
                            with group number N. It will then pass this to next -d/-g or -p
                            filter or print it to the output.

    -h                  -   Show this help and exit.

Example:
    <test.log fdump -g ^query -d user user_queries.txt -d admin admin_queries.txt >rest.txt
```

