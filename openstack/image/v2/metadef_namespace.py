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

from openstack import exceptions
from openstack import resource
from openstack import utils


class MetadefNamespace(resource.Resource):
    resources_key = 'namespaces'
    base_path = '/metadefs/namespaces'

    allow_create = True
    allow_fetch = True
    allow_commit = True
    allow_list = True
    allow_delete = True

    _query_mapping = resource.QueryParameters(
        "limit",
        "marker",
        "resource_types",
        "sort_dir",
        "sort_key",
        "visibility",
    )

    created_at = resource.Body('created_at')
    description = resource.Body('description')
    display_name = resource.Body('display_name')
    is_protected = resource.Body('protected', type=bool)
    namespace = resource.Body('namespace', alternate_id=True)
    owner = resource.Body('owner')
    resource_type_associations = resource.Body(
        'resource_type_associations',
        type=list,
        list_type=dict,
    )
    updated_at = resource.Body('updated_at')
    visibility = resource.Body('visibility')

    def _commit(
        self,
        session,
        request,
        method,
        microversion,
        has_body=True,
        retry_on_conflict=None,
    ):
        # Rather annoyingly, Glance insists on us providing the 'namespace'
        # argument, even if we're not changing it. We need to add this here
        # since it won't be included if Resource.commit thinks its unchanged
        # TODO(stephenfin): Eventually we could indicate attributes that are
        # required in the body on update, like the 'requires_id' and
        # 'create_requires_id' do for the ID in the URL
        request.body['namespace'] = self.namespace

        return super()._commit(
            session,
            request,
            method,
            microversion,
            has_body=True,
            retry_on_conflict=None,
        )

    def _delete_all(self, session, url):
        response = session.delete(url)
        exceptions.raise_from_response(response)
        self._translate_response(response, has_body=False)
        return self

    def delete_all_properties(self, session):
        """Delete all properties in a namespace.

        :param session: The session to use for making this request
        :returns: The server response
        """

        url = utils.urljoin(self.base_path, self.id, 'properties')
        return self._delete_all(session, url)

    def delete_all_objects(self, session):
        """Delete all objects in a namespace.

        :param session: The session to use for making this request
        :returns: The server response
        """
        url = utils.urljoin(self.base_path, self.id, 'objects')
        return self._delete_all(session, url)
