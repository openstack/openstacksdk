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
import numbers
import time

from iso8601 import iso8601
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


class UNIXEpoch(Formatter):

    EPOCH = datetime(1970, 1, 1, tzinfo=iso8601.UTC)

    @classmethod
    def serialize(cls, value):
        """Convert a datetime to a UNIX epoch"""
        if isinstance(value, datetime):
            # Do not try to format using %s as it's platform dependent.
            return (value - cls.EPOCH).total_seconds()
        elif isinstance(value, numbers.Number):
            return value
        else:
            raise ValueError("Unable to serialize UNIX epoch: %s" % value)

    @classmethod
    def deserialize(cls, value):
        """Convert a UNIX epoch into a datetime object"""
        try:
            value = float(value)
        except ValueError:
            raise ValueError("Unable to deserialize UNIX epoch: %s" % value)

        # gmtime doesn't respect microseconds so we need to parse them out
        # if they're there and build the datetime appropriately with the
        # proper precision.
        # NOTES:
        # 1. datetime.fromtimestamp sort of solves this but using localtime
        #    instead of UTC, which we need.
        # 2. On Python 2 we can't just str(value) as it truncates digits
        #    that are significant to us.
        parsed_value = "%000000f" % value
        decimal = parsed_value.find(".")

        if decimal == -1:
            microsecond = 0
        else:
            # Some examples of these timestamps include less precision
            # than the allowable 6 digits that can represent microseconds,
            # so since we have a string we need to construct a real
            # count of microseconds instead of just converting the
            # stringified amount to an int.
            fractional_second = float(parsed_value[decimal:]) * 1e6
            microsecond = int(fractional_second)

        gmt = time.gmtime(value)

        return datetime(*gmt[:6], microsecond=microsecond,
                        tzinfo=iso8601.UTC)


class BoolStr(Formatter):

    @classmethod
    def deserialize(cls, value):
        """Convert a boolean string to a boolean"""
        expr = str(value).lower()
        if "true" == expr:
            return True
        elif "false" == expr:
            return False
        else:
            raise ValueError("Unable to deserialize boolean string: %s"
                             % value)

    @classmethod
    def serialize(cls, value):
        """Convert a boolean to a boolean string"""
        if isinstance(value, bool):
            if value:
                return "true"
            else:
                return "false"
        else:
            raise ValueError("Unable to serialize boolean string: %s"
                             % value)
