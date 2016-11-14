#  Licensed under the Apache License, Version 2.0 (the "License"); you may
#  not use this file except in compliance with the License. You may obtain
#  a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#  License for the specific language governing permissions and limitations
#  under the License.

import argparse

import os_client_config
from os_client_config.tests import base


class TestInit(base.TestCase):
    def test_get_config_without_arg_parser(self):
        cloud_config = os_client_config.get_config(options=None)
        self.assertIsInstance(
            cloud_config,
            os_client_config.cloud_config.CloudConfig
        )

    def test_get_config_with_arg_parser(self):
        cloud_config = os_client_config.get_config(
            options=argparse.ArgumentParser())
        self.assertIsInstance(
            cloud_config,
            os_client_config.cloud_config.CloudConfig
        )
