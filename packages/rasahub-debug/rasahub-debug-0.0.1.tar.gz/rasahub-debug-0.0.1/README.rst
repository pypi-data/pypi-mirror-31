=============
Rasahub-Debug
=============

Rasahub-Debug is a simple socket connector for debugging Rasahub.

----

Prerequisites
=============

* Python installed

Installation
============

Pypi package
------------

Install via pip:

.. code-block:: bash

  pip install rasahub-debug


Usage
=====

Create configuration
--------------------

Create file config.yml in working path. Example:

.. code-block:: yaml

debug1:
  package: 'rasahub_debug'
  classname: 'DebugConnector'
  init:
    host: '127.0.0.1'
    port: 5020
  out: 'debug2'

debug2:
  package: 'rasahub_debug'
  classname: 'DebugConnector'
  init:
    host: '127.0.0.1'
    port: 5021
  out: 'debug1'


Then spawn debuggers (rasahub-debugger-client) on the specified port.


Command-Line API
----------------

Start rasahub:

.. code-block:: bash

  python -m rasahub



* License: MIT
* `PyPi`_ - package installation

.. _PyPi: https://pypi.python.org/pypi/rasahub
