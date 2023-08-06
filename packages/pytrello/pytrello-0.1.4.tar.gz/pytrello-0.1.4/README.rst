========
Overview
========

.. start-badges

.. list-table::
    :stub-columns: 1

    * - docs
      - |docs|
    * - tests
      - | |travis| |appveyor| |requires| |coveralls| |codecov|
    * - package
      - | |version| |wheel| |supported-versions| |supported-implementations|

.. |docs| image:: https://readthedocs.org/projects/python-trello/badge/?style=flat
    :target: https://readthedocs.org/projects/python-trello
    :alt: Documentation Status

.. |travis| image:: https://travis-ci.org/dohlee/python-trello.svg?branch=master
    :alt: Travis-CI Build Status
    :target: https://travis-ci.org/dohlee/python-trello

.. |appveyor| image:: https://ci.appveyor.com/api/projects/status/github/dohlee/python-trello?branch=master&svg=true
    :alt: AppVeyor Build Status
    :target: https://ci.appveyor.com/project/dohlee/python-trello

.. |requires| image:: https://requires.io/github/dohlee/python-trello/requirements.svg?branch=master
    :alt: Requirements Status
    :target: https://requires.io/github/dohlee/python-trello/requirements/?branch=master

.. |coveralls| image:: https://coveralls.io/repos/dohlee/python-trello/badge.svg?branch=master&service=github
    :alt: Coverage Status
    :target: https://coveralls.io/r/dohlee/python-trello

.. |codecov| image:: https://codecov.io/github/dohlee/python-trello/coverage.svg?branch=master
    :alt: Coverage Status
    :target: https://codecov.io/github/dohlee/python-trello

.. |version| image:: https://img.shields.io/pypi/v/pytrello.svg
    :alt: PyPI Package latest release
    :target: https://pypi.python.org/pypi/pytrello

.. |wheel| image:: https://img.shields.io/pypi/wheel/pytrello.svg
    :alt: PyPI Wheel
    :target: https://pypi.python.org/pypi/pytrello

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/pytrello.svg
    :alt: Supported versions
    :target: https://pypi.python.org/pypi/pytrello

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/pytrello.svg
    :alt: Supported implementations
    :target: https://pypi.python.org/pypi/pytrello


.. end-badges

Python wrapper for Trello API. Version v0.1.4.

* Free software: MIT license

Installation
============

::

    pip install pytrello

Documentation
=============

https://python-trello.readthedocs.io/

Development
===========

To run the all tests run::

    tox

Note, to combine the coverage data from all the tox environments run:

.. list-table::
    :widths: 10 90
    :stub-columns: 1

    - - Windows
      - ::

            set PYTEST_ADDOPTS=--cov-append
            tox

    - - Other
      - ::

            PYTEST_ADDOPTS=--cov-append tox
