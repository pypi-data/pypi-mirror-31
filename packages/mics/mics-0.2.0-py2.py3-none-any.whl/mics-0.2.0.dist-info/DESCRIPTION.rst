
========
Overview
========

Mixtures of Independently Collected Samples

* Free software: MIT license

Installation
============

::

    pip install mics

Documentation
=============

https://mics.readthedocs.io/

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



Changelog
=========

0.2.0 (2018-05-09)
------------------

* Implementation of classes ``sample``, ``pool``, ``mixture``, ``MICS`` and ``MBAR``.


0.1.0 (2017-10-11)
------------------

* First release on PyPI.


