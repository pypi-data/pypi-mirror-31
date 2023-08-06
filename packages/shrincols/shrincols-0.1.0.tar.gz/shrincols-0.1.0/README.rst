shrincols
=========

CLI for making a text to fit a max number of columns.

Preparing for Development
-------------------------

1. Ensure ``pip`` and ``pipenv`` are installed.
2. Clone repository: ``https://github.com/thiagolcmelo/desafio-idwall``
3. Fetch development dependencies: ``make install``

Usage
-----

The input might be a filename:

::

    $ shrincols filename.txt -c 80

or a string:

::
    $ shrincols "some text goes here ..." -c 80

The option ``-j`` forces the text to be justified:

::

    $ shrincols filename.txt -c 80 -j

It would be a nice feature to read standard input, we will implement soon.

Running Tests
-------------

Run tests locally using ``make`` if virtualenv is active:

::

    $ make

If virtualenv isn't active then use

::

    $ pipenv run make



