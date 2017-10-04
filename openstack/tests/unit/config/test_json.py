# Copyright (c) 2015 Hewlett-Packard Development Company, L.P.
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

import jsonschema
from testtools import content

from openstack.config import defaults
from openstack.tests.unit.config import base


class TestConfig(base.TestCase):

    def json_diagnostics(self, exc_info):
        self.addDetail('filename', content.text_content(self.filename))
        for error in sorted(self.validator.iter_errors(self.json_data)):
            self.addDetail('jsonschema', content.text_content(str(error)))

    def test_defaults_valid_json(self):
        _schema_path = os.path.join(
            os.path.dirname(os.path.realpath(defaults.__file__)),
            'schema.json')
        schema = json.load(open(_schema_path, 'r'))
        self.validator = jsonschema.Draft4Validator(schema)
        self.addOnException(self.json_diagnostics)

        self.filename = os.path.join(
            os.path.dirname(os.path.realpath(defaults.__file__)),
            'defaults.json')
        self.json_data = json.load(open(self.filename, 'r'))

        self.assertTrue(self.validator.is_valid(self.json_data))

    def test_vendors_valid_json(self):
        _schema_path = os.path.join(
            os.path.dirname(os.path.realpath(defaults.__file__)),
            'vendor-schema.json')
        schema = json.load(open(_schema_path, 'r'))
        self.validator = jsonschema.Draft4Validator(schema)
        self.addOnException(self.json_diagnostics)

        _vendors_path = os.path.join(
            os.path.dirname(os.path.realpath(defaults.__file__)),
            'vendors')
        for self.filename in glob.glob(os.path.join(_vendors_path, '*.json')):
            self.json_data = json.load(open(self.filename, 'r'))

            self.assertTrue(self.validator.is_valid(self.json_data))
