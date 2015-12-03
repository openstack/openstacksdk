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

_json_path = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), 'constructors.json')
_class_mapping = None


def get_constructor_mapping():
    global _class_mapping
    if not _class_mapping:
        with open(_json_path, 'r') as json_file:
            _class_mapping = json.load(json_file)
    return _class_mapping
