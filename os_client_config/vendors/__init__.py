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
import os

import yaml

vendors_path = os.path.dirname(os.path.realpath(__file__))

CLOUD_DEFAULTS = {}
for vendor in glob.glob(os.path.join(vendors_path, '*.yaml')):
    with open(vendor, 'r') as f:
        CLOUD_DEFAULTS.update(yaml.safe_load(f))
