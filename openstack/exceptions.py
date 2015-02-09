# Copyright 2010 Jacob Kaplan-Moss
# Copyright 2011 Nebula, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
"""
Exception definitions.
"""

import six


class SDKException(Exception):
    """The base exception class for all exceptions this library raises."""
    def __init__(self, message=None):
        self.message = self.__class__.__name__ if message is None else message
        super(Exception, self).__init__(self.message)


class AuthorizationFailure(SDKException):
    """Cannot authorize API client."""
    pass


class EndpointException(SDKException):
    """Something is rotten in Service Catalog."""
    pass


class EndpointNotFound(EndpointException):
    """Could not find requested endpoint in Service Catalog."""
    pass


class EmptyCatalog(EndpointNotFound):
    """The service catalog is empty."""
    pass


class NoMatchingPlugin(SDKException):
    """No matching plugins could be created with the provided parameters."""
    pass


class InvalidResponse(SDKException):
    """The response from the server is not valid for this request."""

    def __init__(self, response):
        super(InvalidResponse, self).__init__()
        self.response = response


class HttpException(SDKException):
    def __init__(self, message, details=None, status_code=None):
        super(HttpException, self).__init__(message)
        self.details = details
        self.status_code = status_code

    def __unicode__(self):
        msg = self.__class__.__name__ + ": " + self.message
        if self.details:
            msg += ", " + six.text_type(self.details)
        return msg

    def __str__(self):
        return self.__unicode__()


class MethodNotSupported(SDKException):
    """The resource does not support this operation type."""
    pass


class DuplicateResource(SDKException):
    """More than one resource exists with that name."""
    pass


class ResourceTimeout(SDKException):
    """Timeout waiting for resource."""
    pass


class ResourceFailure(SDKException):
    """General resource failure."""
    pass
