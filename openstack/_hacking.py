# Copyright (c) 2019, Red Hat, Inc.
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

import re

"""
Guidelines for writing new hacking checks

 - Use only for openstacksdk specific tests. OpenStack general tests
   should be submitted to the common 'hacking' module.
 - Pick numbers in the range O3xx. Find the current test with
   the highest allocated number and then pick the next value.
 - Keep the test method code in the source file ordered based
   on the O3xx value.
 - List the new rule in the top level HACKING.rst file
 - Add test cases for each new rule to nova/tests/unit/test_hacking.py

"""

SETUPCLASS_RE = re.compile(r"def setUpClass\(")


def assert_no_setupclass(logical_line):
    """Check for use of setUpClass

    O300
    """
    if SETUPCLASS_RE.match(logical_line):
        yield (0, "O300: setUpClass not allowed")


def factory(register):
    register(assert_no_setupclass)
