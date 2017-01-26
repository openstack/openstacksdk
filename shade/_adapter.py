# Copyright (c) 2016 Red Hat, Inc.
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

''' Wrapper around keystoneauth Session to wrap calls in TaskManager '''

import functools
from keystoneauth1 import adapter
from six.moves import urllib

from shade import exc
from shade import meta
from shade import task_manager


def extract_name(url):
    '''Produce a key name to use in logging/metrics from the URL path.

    We want to be able to logic/metric sane general things, so we pull
    the url apart to generate names. The function returns a list because
    there are two different ways in which the elements want to be combined
    below (one for logging, one for statsd)

    Some examples are likely useful:

    /servers -> ['servers']
    /servers/{id} -> ['servers']
    /servers/{id}/os-security-groups -> ['servers', 'os-security-groups']
    /v2.0/networks.json -> ['networks']
    '''

    url_path = urllib.parse.urlparse(url).path.strip()
    # Remove / from the beginning to keep the list indexes of interesting
    # things consistent
    if url_path.startswith('/'):
        url_path = url_path[1:]

    # Special case for neutron, which puts .json on the end of urls
    if url_path.endswith('.json'):
        url_path = url_path[:-len('.json')]

    url_parts = url_path.split('/')
    if url_parts[-1] == 'detail':
        # Special case detail calls
        # GET /servers/detail
        # returns ['servers', 'detail']
        name_parts = url_parts[-2:]
    else:
        # Strip leading version piece so that
        # GET /v2.0/networks
        # returns ['networks']
        if url_parts[0] in ('v1', 'v2', 'v2.0'):
            url_parts = url_parts[1:]
        name_parts = []
        # Pull out every other URL portion - so that
        # GET /servers/{id}/os-security-groups
        # returns ['servers', 'os-security-groups']
        for idx in range(0, len(url_parts)):
            if not idx % 2 and url_parts[idx]:
                name_parts.append(url_parts[idx])

    # Keystone Token fetching is a special case, so we name it "tokens"
    if url_path.endswith('tokens'):
        name_parts = ['tokens']

    # Getting the root of an endpoint is doing version discovery
    if not name_parts:
        name_parts = ['discovery']

    # Strip out anything that's empty or None
    return [part for part in name_parts if part]


class ShadeAdapter(adapter.Adapter):

    def __init__(self, shade_logger, manager, *args, **kwargs):
        super(ShadeAdapter, self).__init__(*args, **kwargs)
        self.shade_logger = shade_logger
        self.manager = manager

    def _munch_response(self, response, result_key=None):
        exc.raise_from_response(response)

        if not response.content:
            # This doens't have any content
            return response

        # Some REST calls do not return json content. Don't decode it.
        if 'application/json' not in response.headers.get('Content-Type'):
            return response

        try:
            result_json = response.json()
        except Exception:
            return response

        request_id = response.headers.get('x-openstack-request-id')

        if task_manager._is_listlike(result_json):
            return meta.obj_list_to_dict(
                result_json, request_id=request_id)

        # Wrap the keys() call in list() because in python3 keys returns
        # a "dict_keys" iterator-like object rather than a list
        json_keys = list(result_json.keys())
        if len(json_keys) > 1 and result_key:
            result = result_json[result_key]
        elif len(json_keys) == 1:
            result = result_json[json_keys[0]]
        else:
            # Passthrough the whole body - sometimes (hi glance) things
            # come through without a top-level container. Also, sometimes
            # you need to deal with pagination
            result = result_json

        if task_manager._is_listlike(result):
            return meta.obj_list_to_dict(result, request_id=request_id)
        if task_manager._is_objlike(result):
            return meta.obj_to_dict(result, request_id=request_id)
        return result

    def request(self, url, method, run_async=False, *args, **kwargs):
        name_parts = extract_name(url)
        name = '.'.join([self.service_type, method] + name_parts)
        class_name = "".join([
            part.lower().capitalize() for part in name.split('.')])

        request_method = functools.partial(
            super(ShadeAdapter, self).request, url, method)

        class RequestTask(task_manager.BaseTask):

            def __init__(self, **kw):
                super(RequestTask, self).__init__(**kw)
                self.name = name
                self.__class__.__name__ = str(class_name)
                self.run_async = run_async

            def main(self, client):
                self.args.setdefault('raise_exc', False)
                return request_method(**self.args)

        response = self.manager.submit_task(RequestTask(**kwargs))
        if run_async:
            return response
        else:
            return self._munch_response(response)
