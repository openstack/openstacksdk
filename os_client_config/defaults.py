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

import os

import yaml

_yaml_path = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), 'defaults.yaml')
_defaults = None


def get_defaults():
    global _defaults
    if not _defaults:
        # Python language specific defaults
        # These are defaults related to use of python libraries, they are
        # not qualities of a cloud.
        _defaults = dict(
            api_timeout=None,
            verify=True,
            cacert=None,
            cert=None,
            key=None,
        )
        with open(_yaml_path, 'r') as yaml_file:
            updates = yaml.load(yaml_file.read())
            if updates is not None:
                _defaults.update(updates)

    return _defaults.copy()
