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

from openstack import format

from urllib import parse


class HREFToUUID(format.Formatter):

    @classmethod
    def deserialize(cls, value):
        """Convert a HREF to the UUID portion"""
        parts = parse.urlsplit(value)

        # Only try to proceed if we have an actual URI.
        # Just check that we have a scheme, netloc, and path.
        if not all(parts[:3]):
            raise ValueError("Unable to convert %s to an ID" % value)

        # The UUID will be the last portion of the URI.
        return parts.path.split("/")[-1]

    @classmethod
    def serialize(cls, value):
        # NOTE(briancurtin): If we had access to the session to get
        # the endpoint we could do something smart here like take an ID
        # and give back an HREF, but this will just have to be something
        # that works different because Barbican does what it does...
        return value
