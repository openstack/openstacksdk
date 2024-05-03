# Copyright (c) 2014 Hewlett-Packard Development Company, L.P.
#
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

import json
import os
import threading

_json_path = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), 'defaults.json'
)
_defaults = None
_defaults_lock = threading.Lock()


# json_path argument is there for os-client-config
def get_defaults(json_path=_json_path):
    global _defaults
    if _defaults is not None:
        return _defaults.copy()
    with _defaults_lock:
        if _defaults is not None:
            # Did someone else just finish filling it?
            return _defaults.copy()
        # Python language specific defaults
        # These are defaults related to use of python libraries, they are
        # not qualities of a cloud.
        #
        # NOTE(harlowja): update a in-memory dict, before updating
        # the global one so that other callers of get_defaults do not
        # see the partially filled one.
        tmp_defaults = dict(
            api_timeout=None,
            verify=True,
            cacert=None,
            cert=None,
            key=None,
        )
        with open(json_path) as json_file:
            updates = json.load(json_file)
            if updates is not None:
                tmp_defaults.update(updates)
        _defaults = tmp_defaults
        return tmp_defaults.copy()
