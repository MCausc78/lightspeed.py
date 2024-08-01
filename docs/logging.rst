:orphan:

.. currentmodule:: lightspeed
.. versionadded:: 0.6.0
.. _logging_setup:

Setting Up Logging
===================

*lightspeed.py* logs errors and debug information via the :mod:`logging` python
module. In order to streamline this process, the library provides default configuration for the ``lightspeed`` logger when using :meth:`Client.run`. It is strongly recommended that the logging module is configured, as no errors or warnings will be output if it is not set up.

The default logging configuration provided by the library will print to :data:`sys.stderr` using coloured output. You can configure it to send to a file instead by using one of the built-in :mod:`logging.handlers`, such as :class:`logging.FileHandler`.

This can be done by passing it through :meth:`lightspeed.utils.setup_logging`:

.. code-block:: python3

    import logging

    handler = logging.FileHandler(filename='lightspeed.log', encoding='utf-8', mode='w')

    # Assume client refers to a lightspeed.Client subclass...
    lightspeed.utils.setup_logging(handler=handler)
    await client.start(token)

You can also disable the library's logging configuration completely by passing ``None``:

.. code-block:: python3

    lightspeed.utils.setup_logging(handler=None)
    await client.start(token)


Likewise, configuring the log level to ``logging.DEBUG`` is also possible:

.. code-block:: python3

    import logging

    handler = logging.FileHandler(filename='lightspeed.log', encoding='utf-8', mode='w')

    # Assume client refers to a lightspeed.Client subclass...
    lightspeed.utils.setup_logging(handler=handler, level=logging.DEBUG)
    await client.start(token)

This is recommended, especially at verbose levels such as ``DEBUG``, as there are a lot of events logged and it would clog the stderr of your program.

If you want the logging configuration the library provides to affect all loggers rather than just the ``lightspeed`` logger, you can pass ``root_logger=True`` inside :meth:`lightspeed.utils.setup_logging`:

.. code-block:: python3

    lightspeed.utils.setup_logging(handler=handler, root=True)
    

If you want to setup logging using the library provided configuration without using :meth:`Client.run`, you can use :func:`lightspeed.utils.setup_logging`:

.. code-block:: python3

    import lightspeed

    lightspeed.utils.setup_logging()

    # or, for example
    lightspeed.utils.setup_logging(level=logging.INFO, root=False)

More advanced setups are possible with the :mod:`logging` module. The example below configures a rotating file handler that outputs DEBUG output for everything the library outputs, except for HTTP requests:

.. code-block:: python3

    import lightspeed
    import logging
    import logging.handlers

    logger = logging.getLogger('lightspeed')
    logger.setLevel(logging.DEBUG)
    logging.getLogger('lightspeed.http').setLevel(logging.INFO)

    handler = logging.handlers.RotatingFileHandler(
        filename='lightspeed.log',
        encoding='utf-8',
        maxBytes=32 * 1024 * 1024,  # 32 MiB
        backupCount=5,  # Rotate through 5 files
    )
    dt_fmt = '%Y-%m-%d %H:%M:%S'
    formatter = logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', dt_fmt, style='{')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # Assume client refers to a lightspeed.Client subclass...
    # Suppress the default configuration since we have our own
    lightspeed.utils.setup_logging(handler=None)
    await client.start(token)


For more information, check the documentation and tutorial of the :mod:`logging` module.
