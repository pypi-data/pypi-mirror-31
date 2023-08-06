========
Overview
========

.. start-badges

.. list-table::
    :stub-columns: 1

    * - docs
      - |docs|
    * - tests
      - | |travis| |appveyor| |requires|
        | |codecov|
    * - package
      - | |version| |wheel| |supported-versions| |supported-implementations|

.. |docs| image:: https://readthedocs.org/projects/python-biopipe/badge/?style=flat
    :target: https://readthedocs.org/projects/python-biopipe
    :alt: Documentation Status

.. |travis| image:: https://travis-ci.org/dohlee/python-biopipe.svg?branch=master
    :alt: Travis-CI Build Status
    :target: https://travis-ci.org/dohlee/python-biopipe

.. |appveyor| image:: https://ci.appveyor.com/api/projects/status/github/dohlee/python-biopipe?branch=master&svg=true
    :alt: AppVeyor Build Status
    :target: https://ci.appveyor.com/project/dohlee/python-biopipe

.. |requires| image:: https://requires.io/github/dohlee/python-biopipe/requirements.svg?branch=master
    :alt: Requirements Status
    :target: https://requires.io/github/dohlee/python-biopipe/requirements/?branch=master

.. |codecov| image:: https://codecov.io/github/dohlee/python-biopipe/coverage.svg?branch=master
    :alt: Coverage Status
    :target: https://codecov.io/github/dohlee/python-biopipe

.. |version| image:: https://img.shields.io/pypi/v/biopipe.svg
    :alt: PyPI Package latest release
    :target: https://pypi.python.org/pypi/biopipe

.. |wheel| image:: https://img.shields.io/pypi/wheel/biopipe.svg
    :alt: PyPI Wheel
    :target: https://pypi.python.org/pypi/biopipe

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/biopipe.svg
    :alt: Supported versions
    :target: https://pypi.python.org/pypi/biopipe

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/biopipe.svg
    :alt: Supported implementations
    :target: https://pypi.python.org/pypi/biopipe


.. end-badges

Pipeable commandline utilities for simple bioinformatics research. Currently on version v0.1.7.

* Free software: MIT license

Installation
============

::

    pip install biopipe

Documentation
=============

https://python-biopipe.readthedocs.io/

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
