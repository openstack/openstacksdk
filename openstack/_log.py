# Copyright (c) 2015 IBM Corp.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import sys


def setup_logging(name, handlers=None, level=None):
    """Set up logging for a named logger.

    Gets and initializes a named logger, ensuring it at least has a
    `logging.NullHandler` attached.

    :param str name:
      Name of the logger.
    :param list handlers:
      A list of `logging.Handler` objects to attach to the logger.
    :param int level:
      Log level to set the logger at.

    :returns: A `logging.Logger` object that can be used to emit log messages.
    """
    handlers = handlers or []
    log = logging.getLogger(name)
    if len(log.handlers) == 0 and not handlers:
        h = logging.NullHandler()
        log.addHandler(h)
    for h in handlers:
        log.addHandler(h)
    if level:
        log.setLevel(level)
    return log


def enable_logging(
    debug=False, http_debug=False, path=None, stream=None,
    format_stream=False,
    format_template='%(asctime)s %(levelname)s: %(name)s %(message)s',
    handlers=None,
):
    """Enable logging output.

    Helper function to enable logging. This function is available for
    debugging purposes and for folks doing simple applications who want an
    easy 'just make it work for me'. For more complex applications or for
    those who want more flexibility, the standard library ``logging`` package
    will receive these messages in any handlers you create.

    :param bool debug:
        Set this to ``True`` to receive debug messages.
    :param bool http_debug:
        Set this to ``True`` to receive debug messages including
        HTTP requests and responses. This implies ``debug=True``.
    :param str path:
        If a *path* is specified, logging output will written to that file
        in addition to sys.stderr.
        The path is passed to logging.FileHandler, which will append messages
        the file (and create it if needed).
    :param stream:
        One of ``None `` or ``sys.stdout`` or ``sys.stderr``.
        If it is ``None``, nothing is logged to a stream.
        If it isn't ``None``, console output is logged to this stream.
    :param bool format_stream:
        If format_stream is False, the default, apply ``format_template`` to
        ``path`` but not to ``stream`` outputs. If True, apply
        ``format_template`` to ``stream`` outputs as well.
    :param str format_template:
        Template to pass to :class:`logging.Formatter`.

    :rtype: None
    """
    if not stream and not path:
        stream = sys.stdout

    if http_debug:
        debug = True
    if debug:
        level = logging.DEBUG
    else:
        level = logging.INFO

    formatter = logging.Formatter(format_template)

    if handlers:
        for handler in handlers:
            handler.setFormatter(formatter)

    else:
        handlers = []

        if stream is not None:
            console = logging.StreamHandler(stream)
            if format_stream:
                console.setFormatter(formatter)
            handlers.append(console)

        if path is not None:
            file_handler = logging.FileHandler(path)
            file_handler.setFormatter(formatter)
            handlers.append(file_handler)

    setup_logging('openstack', handlers=handlers, level=level)
    setup_logging('keystoneauth', handlers=handlers, level=level)

    # Turn off logging on these so that if loggers higher in the tree
    # are more verbose we only get what we want out of the SDK. This is
    # particularly useful when combined with tools like ansible which set
    # debug logging level at the logging root.
    # If more complex logging is desired including stevedore debug logging,
    # enable_logging should not be used and instead python logging should
    # be configured directly.
    setup_logging(
        'urllib3', handlers=[logging.NullHandler()], level=logging.INFO)
    setup_logging(
        'stevedore', handlers=[logging.NullHandler()], level=logging.INFO)
    # Suppress warning about keystoneauth loggers
    setup_logging('keystoneauth.discovery')
    setup_logging('keystoneauth.identity.base')
    setup_logging('keystoneauth.identity.generic.base')
