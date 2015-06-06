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

import glob
import json
import os

import yaml

_vendors_path = os.path.dirname(os.path.realpath(__file__))
_vendor_defaults = None


def get_profile(profile_name):
    global _vendor_defaults
    if _vendor_defaults is None:
        _vendor_defaults = {}
        for vendor in glob.glob(os.path.join(_vendors_path, '*.yaml')):
            with open(vendor, 'r') as f:
                vendor_data = yaml.safe_load(f)
                _vendor_defaults[vendor_data['name']] = vendor_data['profile']
        for vendor in glob.glob(os.path.join(_vendors_path, '*.json')):
            with open(vendor, 'r') as f:
                vendor_data = json.load(f)
                _vendor_defaults[vendor_data['name']] = vendor_data['profile']
    return _vendor_defaults.get(profile_name)
