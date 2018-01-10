# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import functools
import logging
import time

import deprecation

from openstack import _log
from openstack import exceptions
from openstack import version


def deprecated(deprecated_in=None, removed_in=None,
               details=""):
    """Mark a method as deprecated

    :param deprecated_in: The version string where this method is deprecated.
                          Generally this is the next version to be released.
    :param removed_in: The version where this method will be removed
                       from the code base. Generally this is the next
                       major version. This argument is helpful for the
                       tests when using ``deprecation.fail_if_not_removed``.
    :param str details: Helpful details to callers and the documentation.
                        This will usually be a recommendation for alternate
                        code to use.
    """
    # As all deprecations within this library have the same current_version,
    # return a partial function with the library version always set.
    partial = functools.partial(deprecation.deprecated,
                                current_version=version.__version__)

    # TODO(shade) shade's tags break these - so hard override them for now.
    # We'll want a patch fixing this before we cut any releases.
    removed_in = '2.0.0'
    return partial(deprecated_in=deprecated_in, removed_in=removed_in,
                   details=details)


class NullHandler(logging.Handler):
    def emit(self, record):
        pass


def setup_logging(name):
    '''Get a logging.Logger and make sure there is at least a NullHandler.'''
    log = logging.getLogger(name)
    if len(log.handlers) == 0:
        h = NullHandler()
        log.addHandler(h)
    return log


def enable_logging(debug=False, path=None, stream=None):
    """Enable logging to a file at path and/or a console stream.

    This function is available for debugging purposes. If you wish to
    log this package's message in your application, the standard library
    ``logging`` package will receive these messages in any handlers you
    create.

    :param bool debug: Set this to ``True`` to receive debug messages,
                       which includes HTTP requests and responses,
                       or ``False`` for warning messages.
    :param str path: If a *path* is specified, logging output will
                     written to that file   in addition to sys.stderr.
                     The path is passed to logging.FileHandler,
                     which will append messages the file (and create
                     it if needed).
    :param stream: One of ``None `` or ``sys.stdout`` or ``sys.stderr``.
                   If it is ``None``, nothing is logged to a stream.
                   If it isn't ``None``, console output is logged
                   to this stream.

    :rtype: None
    """
    if path is None and stream is None:
        raise ValueError("path and/or stream must be set")

    logger = logging.getLogger('openstack')
    ksalog = logging.getLogger('keystoneauth')
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s: %(name)s %(message)s')

    if stream is not None:
        console = logging.StreamHandler(stream)
        console.setFormatter(formatter)
        logger.addHandler(console)
        ksalog.addHandler(console)

    if path is not None:
        file_handler = logging.FileHandler(path)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        ksalog.addHandler(file_handler)

    logger.setLevel(logging.DEBUG if debug else logging.WARNING)
    ksalog.setLevel(logging.DEBUG if debug else logging.WARNING)


def urljoin(*args):
    """A custom version of urljoin that simply joins strings into a path.

    The real urljoin takes into account web semantics like when joining a url
    like /path this should be joined to http://host/path as it is an anchored
    link. We generally won't care about that in client.
    """
    return '/'.join(str(a or '').strip('/') for a in args)


def iterate_timeout(timeout, message, wait=2):
    """Iterate and raise an exception on timeout.

    This is a generator that will continually yield and sleep for
    wait seconds, and if the timeout is reached, will raise an exception
    with <message>.

    """
    log = _log.setup_logging('openstack.iterate_timeout')

    try:
        # None as a wait winds up flowing well in the per-resource cache
        # flow. We could spread this logic around to all of the calling
        # points, but just having this treat None as "I don't have a value"
        # seems friendlier
        if wait is None:
            wait = 2
        elif wait == 0:
            # wait should be < timeout, unless timeout is None
            wait = 0.1 if timeout is None else min(0.1, timeout)
        wait = float(wait)
    except ValueError:
        raise exceptions.SDKException(
            "Wait value must be an int or float value. {wait} given"
            " instead".format(wait=wait))

    start = time.time()
    count = 0
    while (timeout is None) or (time.time() < start + timeout):
        count += 1
        yield count
        log.debug('Waiting %s seconds', wait)
        time.sleep(wait)
    raise exceptions.ResourceTimeout(message)
