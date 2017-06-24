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
import six


class Formatter(object):
    @classmethod
    def serialize(cls, value):
        """Return a string representing the formatted value"""
        raise NotImplementedError

    @classmethod
    def deserialize(cls, value):
        """Return a formatted object representing the value"""
        raise NotImplementedError


class BoolStr(Formatter):
    @classmethod
    def deserialize(cls, value):
        """Convert a boolean string to a boolean"""
        if isinstance(value, bool):
            return value
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
        if isinstance(value, six.string_types):
            if str(value).lower() in ["true", "false"]:
                return str(value).lower()
        if isinstance(value, bool):
            if value:
                return "true"
            else:
                return "false"
        else:
            raise ValueError("Unable to serialize boolean string: %s"
                             % value)


class YNBool(Formatter):
    @classmethod
    def deserialize(cls, value):
        """Convert a boolean string to a boolean"""
        if isinstance(value, bool):
            return value
        expr = str(value).lower()
        if "y" == expr:
            return True
        elif "n" == expr:
            return False
        else:
            raise ValueError("Unable to deserialize boolean string: %s"
                             % value)

    @classmethod
    def serialize(cls, value):
        """Convert a boolean to a boolean string"""
        if value in ["Y", "N", "y", "n"]:
            return str(value).upper()
        if isinstance(value, bool):
            if value:
                return "Y"
            else:
                return "N"
        else:
            raise ValueError("Unable to serialize boolean string: %s"
                             % value)


class ListRef(Formatter):
    """A formatter used to serialize/deserialize list reference

    [{"id": "any-id"}] <-> ["any-id"], for example.
    """

    @classmethod
    def deserialize(cls, value):
        """Convert a list primitive to list reference"""
        if isinstance(value, list):
            return [item["id"] for item in value]
        else:
            raise ValueError("Unable to deserialize list reference: %s"
                             % value)

    @classmethod
    def serialize(cls, value):
        """Convert list reference to list primitive"""
        if isinstance(value, list):
            return [{"id": item} for item in value]
        else:
            raise ValueError("Unable to serialize list reference: %s"
                             % value)
