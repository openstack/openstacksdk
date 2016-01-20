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

from datetime import datetime
import six

from oslo_utils import timeutils


class Formatter(object):

    @classmethod
    def serialize(cls, value):
        """Return a string representing the formatted value"""
        raise NotImplementedError

    @classmethod
    def deserialize(cls, value):
        """Return a formatted object representing the value"""
        raise NotImplementedError


class ISO8601(Formatter):

    @classmethod
    def serialize(cls, value):
        """Convert a datetime to an ISO8601 string"""
        if isinstance(value, datetime):
            return value.isoformat()
        elif isinstance(value, six.string_types):
            # If we're already given a string, keep it as-is.
            # This happens when a string comes back in a response body,
            # as opposed to the datetime case above which happens when
            # a user is setting a datetime for a request.
            return value
        else:
            raise ValueError("Unable to serialize ISO8601: %s" % value)

    @classmethod
    def deserialize(cls, value):
        """Convert an ISO8601 string to a datetime object"""
        if isinstance(value, six.string_types):
            return timeutils.parse_isotime(value)
        else:
            raise ValueError("Unable to deserialize ISO8601: %s" % value)


class BoolStr(Formatter):

    # The behavior here primarily exists for the deserialize method
    # to be producing Python booleans.

    @classmethod
    def deserialize(cls, value):
        return cls.convert(value)

    @classmethod
    def serialize(cls, value):
        return cls.convert(value)

    @classmethod
    def convert(cls, value):
        expr = str(value).lower()
        if "true" == expr:
            return True
        elif "false" == expr:
            return False
        else:
            raise ValueError("Unable to convert as boolean: %s" % value)
