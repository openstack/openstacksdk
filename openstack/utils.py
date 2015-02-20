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

import logging
import sys


def enable_logging(debug=False, path=None):
    """Enable logging of messages to sys.stderr

    This function is available for debugging purposes. If you wish to
    log this package's message in your application, the standard library
    ``logging`` package will receive these messages in any handlers you
    create.

    :param bool debug: Set this to ``True`` to receive debug messages,
                       which includes HTTP requests and responses,
                       or ``False`` for warning messages.
    :param str path: If a *path* is specified, logging output will
                     written to that file in addition to sys.stderr.
                     The path is passed to logging.FileHandler,
                     which will append messages the file (and create
                     it if needed). *Default: None*

    :rtype: None
    """
    root_logger = logging.getLogger('')
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s: %(name)s %(message)s')

    console = logging.StreamHandler(sys.stderr)
    console.setFormatter(formatter)
    root_logger.addHandler(console)

    if path is not None:
        file_handler = logging.FileHandler(path)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    root_logger.setLevel(logging.DEBUG if debug else logging.WARNING)


def urljoin(*args):
    """A custom version of urljoin that simply joins strings into a path.

    The real urljoin takes into account web semantics like when joining a url
    like /path this should be joined to http://host/path as it is an anchored
    link. We generally won't care about that in client.
    """
    return '/'.join(str(a or '').strip('/') for a in args)
