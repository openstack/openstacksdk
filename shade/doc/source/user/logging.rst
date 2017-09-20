=======
Logging
=======

`shade` uses `Python Logging`_. As `shade` is a library, it does not
configure logging handlers automatically, expecting instead for that to be
the purview of the consuming application.

Simple Usage
------------

For consumers who just want to get a basic logging setup without thinking
about it too deeply, there is a helper method. If used, it should be called
before any other `shade` functionality.

.. code-block:: python

  import shade
  shade.simple_logging()

`shade.simple_logging` takes two optional boolean arguments:

debug
  Turns on debug logging.

http_debug
  Turns on debug logging as well as debug logging of the underlying HTTP calls.

`shade.simple_logging` also sets up a few other loggers and squelches some
warnings or log messages that are otherwise uninteresting or unactionable by
a `shade` user.

Advanced Usage
--------------

`shade` logs to a set of different named loggers.

Most of the logging is set up to log to the root `shade` logger. There are
additional sub-loggers that are used at times, primarily so that a user can
decide to turn on or off a specific type of logging. They are listed below.

shade.task_manager
  `shade` uses a Task Manager to perform remote calls. The `shade.task_manager`
  logger emits messages at the start and end of each Task announging what
  it is going to run and then what it ran and how long it took. Logging
  `shade.task_manager` is a good way to get a trace of external actions shade
  is taking without full `HTTP Tracing`_.

shade.request_ids
  The `shade.request_ids` logger emits a log line at the end of each HTTP
  interaction with the OpenStack Request ID associated with the interaction.
  This can be be useful for tracking action taken on the server-side if one
  does not want `HTTP Tracing`_.

shade.exc
  If `log_inner_exceptions` is set to True, `shade` will emit any wrapped
  exception to the `shade.exc` logger. Wrapped exceptions are usually
  considered implementation details, but can be useful for debugging problems.

shade.iterate_timeout
  When `shade` needs to poll a resource, it does so in a loop that waits
  between iterations and ultimately timesout. The `shade.iterate_timeout`
  logger emits messages for each iteration indicating it is waiting and for
  how long. These can be useful to see for long running tasks so that one
  can know things are not stuck, but can also be noisy.

shade.http
  `shade` will sometimes log additional information about HTTP interactions
  to the `shade.http` logger. This can be verbose, as it sometimes logs
  entire response bodies.

shade.fnmatch
  `shade` will try to use `fnmatch`_ on given `name_or_id` arguments. It's a
  best effort attempt, so pattern misses are logged to `shade.fnmatch`. A user
  may not be intending to use an fnmatch pattern - such as if they are trying
  to find an image named ``Fedora 24 [official]``, so these messages are
  logged separately.

.. _fnmatch: https://pymotw.com/2/fnmatch/

HTTP Tracing
------------

HTTP Interactions are handled by `keystoneauth`. If you want to enable HTTP
tracing while using `shade` and are not using `shade.simple_logging`,
set the log level of the `keystoneauth` logger to `DEBUG`.

Python Logging
--------------

Python logging is a standard feature of Python and is documented fully in the
Python Documentation, which varies by version of Python.

For more information on Python Logging for Python v2, see
https://docs.python.org/2/library/logging.html.

For more information on Python Logging for Python v3, see
https://docs.python.org/3/library/logging.html.
