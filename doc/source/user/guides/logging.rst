=======
Logging
=======

.. note:: TODO(shade) This document is written from a shade POV. It needs to
          be combined with the existing logging guide, but also the logging
          systems need to be rationalized.

`openstacksdk` uses `Python Logging`_. As `openstacksdk` is a library, it does
not configure logging handlers automatically, expecting instead for that to be
the purview of the consuming application.

Simple Usage
------------

For consumers who just want to get a basic logging setup without thinking
about it too deeply, there is a helper method. If used, it should be called
before any other openstacksdk functionality.

.. autofunction:: openstack.enable_logging

.. code-block:: python

  import openstack
  openstack.enable_logging()

The ``stream`` parameter controls the stream where log message are written to.
It defaults to `sys.stdout` which will result in log messages being written
to STDOUT. It can be set to another output stream, or to ``None`` to disable
logging to the console.

The ``path`` parameter sets up logging to log to a file. By default, if
``path`` is given and ``stream`` is not, logging will only go to ``path``.

You can combine the ``path`` and ``stream`` parameters to log to both places
simultaneously.

To log messages to a file called ``openstack.log`` and the console on
``stdout``:

.. code-block:: python

    import sys
    from openstack import utils

    utils.enable_logging(debug=True, path='openstack.log', stream=sys.stdout)


`openstack.enable_logging` also sets up a few other loggers and
squelches some warnings or log messages that are otherwise uninteresting or
unactionable by an openstacksdk user.

Advanced Usage
--------------

`openstacksdk` logs to a set of different named loggers.

Most of the logging is set up to log to the root ``openstack`` logger.
There are additional sub-loggers that are used at times, primarily so that a
user can decide to turn on or off a specific type of logging. They are listed
below.

openstack.config
  Issues pertaining to configuration are logged to the ``openstack.config``
  logger.

openstack.task_manager
  `openstacksdk` uses a Task Manager to perform remote calls. The
  ``openstack.task_manager`` logger emits messages at the start and end
  of each Task announcing what it is going to run and then what it ran and
  how long it took. Logging ``openstack.task_manager`` is a good way to
  get a trace of external actions `openstacksdk` is taking without full
  `HTTP Tracing`_.

openstack.iterate_timeout
  When `openstacksdk` needs to poll a resource, it does so in a loop that waits
  between iterations and ultimately times out. The
  ``openstack.iterate_timeout`` logger emits messages for each iteration
  indicating it is waiting and for how long. These can be useful to see for
  long running tasks so that one can know things are not stuck, but can also
  be noisy.

openstack.fnmatch
  `openstacksdk` will try to use `fnmatch`_ on given `name_or_id` arguments.
  It's a best effort attempt, so pattern misses are logged to
  ``openstack.fnmatch``. A user may not be intending to use an fnmatch
  pattern - such as if they are trying to find an image named
  ``Fedora 24 [official]``, so these messages are logged separately.

.. _fnmatch: https://pymotw.com/2/fnmatch/

HTTP Tracing
------------

HTTP Interactions are handled by `keystoneauth`_. If you want to enable HTTP
tracing while using openstacksdk and are not using `openstack.enable_logging`,
set the log level of the ``keystoneauth`` logger to ``DEBUG``.

For more information see https://docs.openstack.org/keystoneauth/latest/using-sessions.html#logging

.. _keystoneauth: https://docs.openstack.org/keystoneauth/latest/

Python Logging
--------------

Python logging is a standard feature of Python and is documented fully in the
Python Documentation, which varies by version of Python.

For more information on Python Logging for Python v2, see
https://docs.python.org/2/library/logging.html.

For more information on Python Logging for Python v3, see
https://docs.python.org/3/library/logging.html.
