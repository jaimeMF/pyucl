.. module:: ucl

pyucl
=====

`pyucl` is a Python wrapper for the `libucl <https://github.com/vstakhov/libucl>`_ library, which parses data in the `UCL` format.
The :mod:`ucl` module exposes an interface similar to the standard library module :mod:`json` for handling this format.

Loading data from an `UCL` string:

.. code:: python

    >>> import ucl
    >>> ucl.loads('verbose = yes; languages = [es, en]')
    {'languages': ['es', 'en'], 'verbose': True}

Serializing a python object in UCL or JSON format

.. code:: python

    >>> import ucl
    >>> print(ucl.dumps({'languages': ['es', 'en'], 'verbose': True}))
    verbose = true;
    languages [
        "es",
        "en",
    ]
    >>> print(ucl.dumps({'languages': ['es', 'en'], 'verbose': True}, emit_type='json_compact'))
    {"verbose":true,"languages":["es","en"]}

API
---

.. autofunction:: loads

.. autofunction:: load

.. autofunction:: dumps

.. autofunction:: dump

.. autoexception:: UCLDecoderError

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

