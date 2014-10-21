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


class BoolStr(object):
    """A custom boolean/string hybrid type for resource.props.

    Translates a given value to the desired type.
    """
    def __init__(self, given):
        """A boolean parser.

        Interprets the given value as a boolean, ignoring whitespace and case.
        A TypeError is raised when interpreted as neither True nor False.
        """
        expr = str(given).lower()
        if 'true' == expr:
            self.parsed = True
        elif 'false' == expr:
            self.parsed = False
        else:
            msg = 'Invalid as boolean: %s' % given
            raise ValueError(msg)

    def __bool__(self):
        return self.parsed

    __nonzero__ = __bool__

    def __str__(self):
        return str(self.parsed)
