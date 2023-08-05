pypicf - PYPI Classifiers for Humans
====================================

|forthebadge|

::

    ________     ___    ___  ________    ___      ________      ________
    |\   __  \   |\  \  /  /||\   __  \  |\  \    |\   ____\    |\  _____\
    \ \  \|\  \  \ \  \/  / /\ \  \|\  \ \ \  \   \ \  \___|    \ \  \__/
     \ \   ____\  \ \    / /  \ \   ____\ \ \  \   \ \  \        \ \   __\
      \ \  \___|   \/  /  /    \ \  \___|  \ \  \   \ \  \____    \ \  \_|
       \ \__\    __/  / /       \ \__\      \ \__\   \ \_______\   \ \__\
        \|__|   |\___/ /         \|__|       \|__|    \|_______|    \|__|
                \|___|/


📄 Overview
---------------------------

The pypicf is an **interactive tool** that asks some questions about the
`**PYPI
Classifiers** <https://pypi.org/pypi?%3Aaction=list_classifiers>`__ of
your Python product, and then generates **classifiers list** for the
insert to the ``setup.py`` script.

Powered by
`**python-inquirer** <https://github.com/magmax/python-inquirer>`__.

DEMO
~~~~

|DEMO|

✏️ Usage
---------------

Running the pypicf is simple.

::

    $ pypicf

selection
~~~~~~~~~

The pypicf asks you of the classifier by **selection**. In this case,
you can **scroll** the choices by '↑', '↓' arrow key, and then select
the choices by put the **Enter** key.

Example:

::

    [?] What your product Development Status? ('↑', '↓':Select):
    > Development Status :: 1 - Planning
      Development Status :: 2 - Pre-Alpha
      Development Status :: 3 - Alpha
      Development Status :: 4 - Beta
      Development Status :: 5 - Production/Stable
      Development Status :: 6 - Mature
      Development Status :: 7 - Inactive

checkbox
~~~~~~~~

The pypicf asks you of the classifier by the **checkbox**. In this case,
you can **scroll** the choices by '↑', '↓' arrow key, and then **check**
the checkbox by '→', '←' arrow key.

Example:

::

    [?] What the Programming Language you implemented?: python
    [?] Please check the following checkbox ('↑', '↓':Select, '→','←':Choose):
       X Programming Language :: Python
       o Programming Language :: Python :: 2
     > X Programming Language :: Python :: 2.3
       o Programming Language :: Python :: 2.4
       o Programming Language :: Python :: 2.5
       o Programming Language :: Python :: 2.6
       o Programming Language :: Python :: 2.7
       o Programming Language :: Python :: 2 :: Only

📥 Installation
--------------------------

::

    $ pip install pypicf

or

::

    $ git clone git@github.com:alice1017/pypicf.git
    $ cd pypicf
    $ python setup.py build install

👀 Contribution
-------------------

1. Forks on `Github <https://github.com/alice1017/pypicf>`__
2. Find a bug? Send a pull request to get it merged and published.

.. |forthebadge| image:: http://forthebadge.com/images/badges/made-with-python.svg
   :target: http://forthebadge.com
.. |DEMO| image:: https://asciinema.org/a/176872.png
   : target: https://asciinema.org/a/176872
