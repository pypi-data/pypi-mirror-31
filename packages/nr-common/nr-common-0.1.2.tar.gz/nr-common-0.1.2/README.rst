
nr-common
=========


.. image:: https://travis-ci.org/nitred/nr-common.svg?branch=master
   :target: https://travis-ci.org/nitred/nr-common
   :alt: Build Status


Common python functionalities aimed to be at least compatible with Python3.

Current Stable Version
~~~~~~~~~~~~~~~~~~~~~~

.. code-block::

   0.1.2

Installation
============

pip
^^^

.. code-block::

   pip install nr-common

Development Installation
^^^^^^^^^^^^^^^^^^^^^^^^


* Clone the project.
* Install in Anaconda3 environment
  .. code-block::

     $ conda env create --force -f dev_environment.yml
     $ source activate nr-common
     $ pip install -e .

Test
====

To run the tests:

.. code-block::

   make test

Examples
========

.. code-block::

   $ python examples/simple.py

License
=======

MIT
