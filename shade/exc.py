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

import sys

from shade import _log


class OpenStackCloudException(Exception):

    log_inner_exceptions = False

    def __init__(self, message, extra_data=None):
        args = [message]
        if extra_data:
            args.append(extra_data)
        super(OpenStackCloudException, self).__init__(*args)
        self.extra_data = extra_data
        self.inner_exception = sys.exc_info()
        self.orig_message = message

    def log_error(self, logger=None):
        if not logger:
            logger = _log.setup_logging(__name__)
        if self.inner_exception and self.inner_exception[1]:
            logger.error(self.orig_message, exc_info=self.inner_exception)

    def __str__(self):
        message = Exception.__str__(self)
        if self.extra_data is not None:
            message = "%s (Extra: %s)" % (message, self.extra_data)
        if (self.inner_exception and self.inner_exception[1]
                and not self.orig_message.endswith(
                    str(self.inner_exception[1]))):
            message = "%s (Inner Exception: %s)" % (
                message,
                str(self.inner_exception[1]))
        if self.log_inner_exceptions:
            self.log_error()
        return message


class OpenStackCloudTimeout(OpenStackCloudException):
    pass


class OpenStackCloudUnavailableExtension(OpenStackCloudException):
    pass


class OpenStackCloudUnavailableFeature(OpenStackCloudException):
    pass


class OpenStackCloudResourceNotFound(OpenStackCloudException):
    pass


class OpenStackCloudURINotFound(OpenStackCloudException):
    pass
