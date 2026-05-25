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

from typing import Any, Self
from urllib import parse

from keystoneauth1 import adapter

from openstack import resource


class Template(resource.Resource):
    # capabilities
    allow_create = False
    allow_list = False
    allow_fetch = False
    allow_delete = False
    allow_commit = False

    # Properties
    #: The description specified in the template
    description = resource.Body('Description')
    #: Key and value pairs that contain template parameters
    parameters = resource.Body('Parameters', type=dict)
    #: A list of parameter groups each contains a lsit of parameter names.
    parameter_groups = resource.Body('ParameterGroups', type=list)

    def validate(
        self,
        session: adapter.Adapter,
        template: dict[str, Any] | None,
        environment: dict[str, Any] | None = None,
        template_url: str | None = None,
        ignore_errors: str | None = None,
    ) -> Self:
        url = '/validate'

        body: dict[str, Any] = {'template': template}
        if environment is not None:
            body['environment'] = environment
        if template_url is not None:
            body['template_url'] = template_url
        if ignore_errors:
            qry = parse.urlencode({'ignore_errors': ignore_errors})
            url = '?'.join([url, qry])

        resp = session.post(url, json=body)
        self._translate_response(resp)
        return self
