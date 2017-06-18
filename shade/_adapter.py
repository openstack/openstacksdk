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

from shade import _log
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
        self.request_log = _log.setup_logging('shade.request_ids')

    def _log_request_id(self, response, obj=None):
        # Log the request id and object id in a specific logger. This way
        # someone can turn it on if they're interested in this kind of tracing.
        request_id = response.headers.get('x-openstack-request-id')
        if not request_id:
            return response
        tmpl = "{meth} call to {service} for {url} used request id {req}"
        kwargs = dict(
            meth=response.request.method,
            service=self.service_type,
            url=response.request.url,
            req=request_id)

        if isinstance(obj, dict):
            obj_id = obj.get('id', obj.get('uuid'))
            if obj_id:
                kwargs['obj_id'] = obj_id
                tmpl += " returning object {obj_id}"
        self.request_log.debug(tmpl.format(**kwargs))
        return response

    def _munch_response(self, response, result_key=None, error_message=None):
        exc.raise_from_response(response, error_message=error_message)

        if not response.content:
            # This doens't have any content
            return self._log_request_id(response)

        # Some REST calls do not return json content. Don't decode it.
        if 'application/json' not in response.headers.get('Content-Type'):
            return self._log_request_id(response)

        try:
            result_json = response.json()
        except Exception:
            return self._log_request_id(response)

        # Note(rods): this is just a temporary step needed until we
        # don't update all the other REST API calls
        if isinstance(result_json, dict):
            for key in ['volumes', 'volume', 'volumeAttachment', 'backups',
                        'volume_types', 'volume_type_access', 'snapshots',
                        'network', 'networks', 'subnet', 'subnets',
                        'router', 'routers', 'floatingip', 'floatingips',
                        'floating_ip', 'floating_ips', 'port', 'ports',
                        'stack', 'stacks', 'zones', 'events',
                        'security_group', 'security_groups',
                        'security_group_rule', 'security_group_rules',
                        'users', 'user', 'projects', 'tenants',
                        'project', 'tenant']:
                if key in result_json.keys():
                    self._log_request_id(response)
                    return result_json

        if isinstance(result_json, list):
            self._log_request_id(response)
            return meta.obj_list_to_munch(result_json)

        result = None
        if isinstance(result_json, dict):
            # Wrap the keys() call in list() because in python3 keys returns
            # a "dict_keys" iterator-like object rather than a list
            json_keys = list(result_json.keys())
            if len(json_keys) > 1 and result_key:
                result = result_json[result_key]
            elif len(json_keys) == 1:
                result = result_json[json_keys[0]]
        if result is None:
            # Passthrough the whole body - sometimes (hi glance) things
            # come through without a top-level container. Also, sometimes
            # you need to deal with pagination
            result = result_json

        self._log_request_id(response, result)

        if isinstance(result, list):
            return meta.obj_list_to_munch(result)
        elif isinstance(result, dict):
            return meta.obj_to_munch(result)
        return result

    def request(
            self, url, method, run_async=False, error_message=None,
            *args, **kwargs):
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
            return self._munch_response(response, error_message=error_message)
