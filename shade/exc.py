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

import munch
from requests import exceptions as _rex

from shade import _log


class OpenStackCloudException(Exception):

    log_inner_exceptions = False

    def __init__(self, message, extra_data=None, **kwargs):
        args = [message]
        if extra_data:
            if isinstance(extra_data, munch.Munch):
                extra_data = extra_data.toDict()
            args.append("Extra: {0}".format(str(extra_data)))
        super(OpenStackCloudException, self).__init__(*args, **kwargs)
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


class OpenStackCloudHTTPError(OpenStackCloudException, _rex.HTTPError):

    def __init__(self, *args, **kwargs):
        OpenStackCloudException.__init__(self, *args, **kwargs)
        _rex.HTTPError.__init__(self, *args, **kwargs)


class OpenStackCloudBadRequest(OpenStackCloudHTTPError):
    """There is something wrong with the request payload.

    Possible reasons can include malformed json or invalid values to parameters
    such as flavorRef to a server create.
    """


class OpenStackCloudURINotFound(OpenStackCloudHTTPError):
    pass

# Backwards compat
OpenStackCloudResourceNotFound = OpenStackCloudURINotFound


# Logic shamelessly stolen from requests
def raise_from_response(response, error_message=None):
    msg = ''
    if error_message:
        msg = _
    if 400 <= response.status_code < 500:
        source = "Client"
    elif 500 <= response.status_code < 600:
        source = "Server"
    else:
        source = None

    if response.reason:
        remote_error = "Error: {reason} for {url}".format(
            reason=response.reason,
            url=response.url)
    else:
        remote_error = "Error for url: {url}".format(url=response.url)

    if source:
        if error_message:
            msg = '{error_message}. ({code}) {source} {remote_error}'.format(
                error_message=error_message,
                source=source,
                code=response.status_code,
                remote_error=remote_error)
        else:
            msg = '({code}) {source} {remote_error}'.format(
                code=response.status_code,
                source=source,
                remote_error=remote_error)

    # Special case 404 since we raised a specific one for neutron exceptions
    # before
    if response.status_code == 404:
        raise OpenStackCloudURINotFound(msg, response=response)
    elif response.status_code == 400:
        raise OpenStackCloudBadRequest(msg, response=response)
    if msg:
        raise OpenStackCloudHTTPError(msg, response=response)
