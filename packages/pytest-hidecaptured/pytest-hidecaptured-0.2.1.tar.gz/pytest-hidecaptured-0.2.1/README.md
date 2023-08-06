# pytest-hidecaptured

I write tests that generate a lot of debug messages to console and file.
pytest captures all output from tests and displays them when a test fails.
This behavior is exacerbated when there are a large number of tests within a
test run. Since I already log these messages to file I don't need pytest to
display them on the console. I'd rather it showed me its own reports only.

This issue is exacerbated when others run the same tests. All they care about
is whether the test passed or failed and don't need to see the details. In case
the test failed the debug log files already have the required information.

When any test fails pytest displays all captured output (stdout, stderr, log)
as part of its report. For example,

    ===== test session starts ======
    platform darwin -- Python 3.5.1, pytest-2.8.5, py-1.4.31, pluggy-0.3.1
    rootdir: /home/example/code, inifile:
    collected 1 items

    test_logging.py F

    ===== FAILURES =====
    ----- test_logging -----

        def test_logging():
            logger.debug('DEBUG!')
            logger.info('INFO!')
            logger.warning('WARNING!')
            logger.error('ERROR!')
            logger.critical('CRITICAL!')
    >       assert False
    E       assert False

    test_logging.py:33: AssertionError
    ----- Captured stderr call -----
    2016-01-19 22:29:40,581 : test_logging : test_logging : test_logging : DEBUG : DEBUG!
    2016-01-19 22:29:40,582 : test_logging : test_logging : test_logging : INFO : INFO!
    2016-01-19 22:29:40,582 : test_logging : test_logging : test_logging : WARNING : WARNING!
    2016-01-19 22:29:40,582 : test_logging : test_logging : test_logging : ERROR : ERROR!
    2016-01-19 22:29:40,582 : test_logging : test_logging : test_logging : CRITICAL : CRITICAL!
    ===== 1 failed in 0.03 seconds =====

pytest-hidecaptured removes the captured output so it is not displayed. For
example, with pytest-hidecaputred installed, the report for the same test is,

    ===== test session starts ======
    platform darwin -- Python 3.5.1, pytest-2.8.5, py-1.4.31, pluggy-0.3.1
    rootdir: /home/example/code, inifile:
    plugins: hidecaptured-0.1.0
    collected 1 items

    test_logging.py F

    ===== FAILURES =====
    ----- test_logging -----

        def test_logging():
            logger.debug('DEBUG!')
            logger.info('INFO!')
            logger.warning('WARNING!')
            logger.error('ERROR!')
            logger.critical('CRITICAL!')
    >       assert False
    E       assert False

    test_logging.py:33: AssertionError
    ===== 1 failed in 0.02 seconds =====

This [pytest](https://github.com/pytest-dev/pytest) plugin was generated with
[Cookiecutter](https://github.com/audreyr/cookiecutter) along with
[@hackebrot](https://github.com/hackebrot)'s
[Cookiecutter-pytest-plugin](https://github.com/pytest-dev/cookiecutter-pytest-plugin)
template.


# Requirements

* Python 2.7 or 3.3+
* pytest 2.8.5+

Note: Older versions of pytest may be compatible but I have not tested them.

# Installation

You can install *pytest-hidecaptured* with ``pip`` from [PyPI](https://pypi.org/),

    $ pip install pytest-hidecaptured

# Usage

After installing pytest-hidecaputred use ``pytest`` the way you always have.
There is no additional step required and no additional flag(s) added.

# Contributing

Contributions are very welcome. Tests can be run with ``tox``, please ensure
the coverage at least stays the same before you submit a pull request.

# License

Distributed under the terms of the MIT license, "pytest-hidecaptured" is free
and open source software

# Issues

If you encounter any problems, please
[file an issue](https://github.com/codeghar/pytest-hidecaptured/issues)
along with a detailed description.

# Development

The following targets in *Makefile* help do simple things.

## init

    $ make init

Install required packages for development.

## build

    $ make build

Build source distribution and universal wheel.

## test

    $ make test

Runs ``tox`` to run tests.

## release

    $ make release

Upload builds to PyPI. Requires *~/.pypirc* is configured properly.
