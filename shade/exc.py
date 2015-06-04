# Copyright (c) 2015 Hewlett-Packard Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


class OpenStackCloudException(Exception):
    def __init__(self, message, extra_data=None):
        args = [message]
        if extra_data:
            args.append(extra_data)
        super(OpenStackCloudException, self).__init__(*args)
        self.extra_data = extra_data

    def __str__(self):
        if self.extra_data is not None:
            return "%s (Extra: %s)" % (
                Exception.__str__(self), self.extra_data)
        return Exception.__str__(self)


class OpenStackCloudTimeout(OpenStackCloudException):
    pass


class OpenStackCloudUnavailableService(OpenStackCloudException):
    pass


class OpenStackCloudUnavailableExtension(OpenStackCloudException):
    pass


class OpenStackCloudUnavailableFeature(OpenStackCloudException):
    pass
