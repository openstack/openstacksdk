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

from openstack import exceptions

OpenStackCloudException = exceptions.SDKException


class OpenStackCloudUnavailableExtension(OpenStackCloudException):
    pass


class OpenStackCloudUnavailableFeature(OpenStackCloudException):
    pass


# Backwards compat. These are deprecated and should not be used in new code.
class OpenStackCloudCreateException(OpenStackCloudException):
    def __init__(self, resource, resource_id, extra_data=None, **kwargs):
        super().__init__(
            message=f"Error creating {resource}: {resource_id}",
            extra_data=extra_data,
            **kwargs,
        )
        self.resource_id = resource_id


OpenStackCloudTimeout = exceptions.ResourceTimeout
OpenStackCloudHTTPError = exceptions.HttpException
OpenStackCloudBadRequest = exceptions.BadRequestException
OpenStackCloudURINotFound = exceptions.NotFoundException
OpenStackCloudResourceNotFound = OpenStackCloudURINotFound
