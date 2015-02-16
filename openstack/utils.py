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

import collections
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


class CaseInsensitiveDict(collections.MutableMapping):
    """A case insensitive dict for handling properties

    In order to have resource.prop work properly for header keys,
    the attribute dictionary in resource.Resource has to
    be case insensitive. This class implements a MutableMapping
    that stores an unmodified dictionary of user-set keys and
    values, and an internal mapping of the user-set keys to
    their lower case equivalent.
    """

    def __init__(self, parent=None):
        if parent is not None:
            self._keys = dict((key.lower(), key) for key in parent)
        else:
            self._keys = {}
        self._dict = parent or {}

    def __getitem__(self, key):
        if key is None:
            raise KeyError("key is None")

        return self._dict[self._keys[key.lower()]]

    def __setitem__(self, key, value):
        if key is None:
            raise KeyError("key is None")

        self._dict[key] = value
        self._keys[key.lower()] = key

    def __delitem__(self, key):
        if key is None:
            raise KeyError("key is None")

        del self._dict[self._keys[key.lower()]]

    def __contains__(self, key):
        try:
            key = self._keys[key.lower()]
        except KeyError:
            return False
        return key in self._dict

    def __iter__(self):
        return iter(self._dict)

    def __len__(self):
        return len(self._dict)

    def __repr__(self):
        return repr(self._dict)

    def copy(self):
        return CaseInsensitiveDict(self._dict.copy())
