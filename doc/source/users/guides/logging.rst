Logging
=======

Logging can save you time and effort when developing your code or looking
for help. If your code is not behaving how you expect it to, enabling and
configuring logging can quickly give you valuable insight into the root
cause of the issue. If you need help from the OpenStack community, the
logs can help the people there assist you.

.. note:: By default, no logging is done.

Enable SDK Logging
------------------

To enable logging you use :func:`~openstack.utils.enable_logging`.

The ``debug`` parameter controls the logging level. Set ``debug=True`` to
log debug and higher messages. Set ``debug=False`` to log warning and higher
messages.

To log debug and higher messages::

    import sys
    from openstack import utils

    utils.enable_logging(debug=True, stream=sys.stdout)

The ``path`` parameter controls the location of a log file. If set, this
parameter will send log messages to a file using a :py:class:`~logging.FileHandler`.

To log messages to a file called ``openstack.log``::

    from openstack import utils

    utils.enable_logging(debug=True, path='openstack.log')

The ``stream`` parameter controls the stream where log message are written to.
If set to ``sys.stdout`` or ``sys.stderr``, this parameter will send log
messages to that stream using a :py:class:`~logging.StreamHandler`

To log messages to the console on ``stdout``::

    import sys
    from openstack import utils

    utils.enable_logging(debug=True, stream=sys.stdout)

You can combine the ``path`` and ``stream`` parameters to log to both places
simultaneously.

To log messages to a file called ``openstack.log`` and the console on
``stdout``::

    import sys
    from openstack import utils

    utils.enable_logging(debug=True, path='openstack.log', stream=sys.stdout)


Enable requests Logging
-----------------------

The SDK depends on a small number other libraries. Notably, it uses
`requests <https://pypi.python.org/pypi/requests>`_ for its transport layer.
To get even more information about the request/response cycle, you enable
logging of requests the same as you would any other library.

To log messages to the console on ``stdout``::

    import logging
    import sys

    logger = logging.getLogger('requests')
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s: %(name)s %(message)s')
    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(formatter)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(console)
