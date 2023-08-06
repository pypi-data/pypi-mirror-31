============
Rasahub-Rasa
============

Rasahub-Humhubs implements a connector between Rasahub and `Rasa_Core`_ .

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

  pip install rasahub-rasa


Usage
=====

Create configuration
--------------------

Create file config.yml in working path. Example:

.. code-block:: yaml

  rasa:
    host: '127.0.0.1'
    port: 5020


Command-Line API
----------------

Start rasahub:

.. code-block:: bash

  python -m rasahub



Configuring Rasa
================

In your Rasa bots run.py just import the channel using

.. code-block:: python

  from rasahub.rasahubchannel import RasahubInputChannel


And let the agent handle the channel:

.. code-block:: python

  agent.handle_channel(RasahubInputChannel('127.0.0.1', 5020))



* License: MIT
* `PyPi`_ - package installation

.. _Rasa_Core: https://github.com/RasaHQ/rasa_core
.. _PyPi: https://pypi.python.org/pypi/rasahub
