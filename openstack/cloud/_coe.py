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

# import types so that we can reference ListType in sphinx param declarations.
# We can't just use list, because sphinx gets confused by
# openstack.resource.Resource.list and openstack.resource2.Resource.list
import types  # noqa

from openstack.cloud import exc
from openstack.cloud import _normalize
from openstack.cloud import _utils


class CoeCloudMixin(_normalize.Normalizer):

    @property
    def _container_infra_client(self):
        if 'container-infra' not in self._raw_clients:
            self._raw_clients['container-infra'] = self._get_raw_client(
                'container-infra')
        return self._raw_clients['container-infra']

    @_utils.cache_on_arguments()
    def list_coe_clusters(self):
        """List COE(Ccontainer Orchestration Engine) cluster.

        :returns: a list of dicts containing the cluster.

        :raises: ``OpenStackCloudException``: if something goes wrong during
            the OpenStack API call.
        """
        with _utils.shade_exceptions("Error fetching cluster list"):
            data = self._container_infra_client.get('/clusters')
        return self._normalize_coe_clusters(
            self._get_and_munchify('clusters', data))

    def search_coe_clusters(
            self, name_or_id=None, filters=None):
        """Search COE cluster.

        :param name_or_id: cluster name or ID.
        :param filters: a dict containing additional filters to use.
        :param detail: a boolean to control if we need summarized or
            detailed output.

        :returns: a list of dict containing the cluster

        :raises: ``OpenStackCloudException``: if something goes wrong during
            the OpenStack API call.
        """
        coe_clusters = self.list_coe_clusters()
        return _utils._filter_list(
            coe_clusters, name_or_id, filters)

    def get_coe_cluster(self, name_or_id, filters=None):
        """Get a COE cluster by name or ID.

        :param name_or_id: Name or ID of the cluster.
        :param filters:
            A dictionary of meta data to use for further filtering. Elements
            of this dictionary may, themselves, be dictionaries. Example::

                {
                  'last_name': 'Smith',
                  'other': {
                      'gender': 'Female'
                  }
                }

            OR
            A string containing a jmespath expression for further filtering.
            Example:: "[?last_name==`Smith`] | [?other.gender]==`Female`]"

        :returns: A cluster dict or None if no matching cluster is found.
        """
        return _utils._get_entity(self, 'coe_cluster', name_or_id,
                                  filters=filters)

    def create_coe_cluster(
            self, name, cluster_template_id, **kwargs):
        """Create a COE cluster based on given cluster template.

        :param string name: Name of the cluster.
        :param string image_id: ID of the cluster template to use.

        Other arguments will be passed in kwargs.

        :returns: a dict containing the cluster description

        :raises: ``OpenStackCloudException`` if something goes wrong during
            the OpenStack API call
        """
        error_message = ("Error creating cluster of name"
                         " {cluster_name}".format(cluster_name=name))
        with _utils.shade_exceptions(error_message):
            body = kwargs.copy()
            body['name'] = name
            body['cluster_template_id'] = cluster_template_id

            cluster = self._container_infra_client.post(
                '/clusters', json=body)

        self.list_coe_clusters.invalidate(self)
        return cluster

    def delete_coe_cluster(self, name_or_id):
        """Delete a COE cluster.

        :param name_or_id: Name or unique ID of the cluster.
        :returns: True if the delete succeeded, False if the
            cluster was not found.

        :raises: OpenStackCloudException on operation error.
        """

        cluster = self.get_coe_cluster(name_or_id)

        if not cluster:
            self.log.debug(
                "COE Cluster %(name_or_id)s does not exist",
                {'name_or_id': name_or_id},
                exc_info=True)
            return False

        with _utils.shade_exceptions("Error in deleting COE cluster"):
            self._container_infra_client.delete(
                '/clusters/{id}'.format(id=cluster['id']))
            self.list_coe_clusters.invalidate(self)

        return True

    @_utils.valid_kwargs('node_count')
    def update_coe_cluster(self, name_or_id, operation, **kwargs):
        """Update a COE cluster.

        :param name_or_id: Name or ID of the COE cluster being updated.
        :param operation: Operation to perform - add, remove, replace.

        Other arguments will be passed with kwargs.

        :returns: a dict representing the updated cluster.

        :raises: OpenStackCloudException on operation error.
        """
        self.list_coe_clusters.invalidate(self)
        cluster = self.get_coe_cluster(name_or_id)
        if not cluster:
            raise exc.OpenStackCloudException(
                "COE cluster %s not found." % name_or_id)

        if operation not in ['add', 'replace', 'remove']:
            raise TypeError(
                "%s operation not in 'add', 'replace', 'remove'" % operation)

        patches = _utils.generate_patches_from_kwargs(operation, **kwargs)
        # No need to fire an API call if there is an empty patch
        if not patches:
            return cluster

        with _utils.shade_exceptions(
                "Error updating COE cluster {0}".format(name_or_id)):
            self._container_infra_client.patch(
                '/clusters/{id}'.format(id=cluster['id']),
                json=patches)

        new_cluster = self.get_coe_cluster(name_or_id)
        return new_cluster

    def get_coe_cluster_certificate(self, cluster_id):
        """Get details about the CA certificate for a cluster by name or ID.

        :param cluster_id: ID of the cluster.

        :returns: Details about the CA certificate for the given cluster.
        """
        msg = ("Error fetching CA cert for the cluster {cluster_id}".format(
               cluster_id=cluster_id))
        url = "/certificates/{cluster_id}".format(cluster_id=cluster_id)
        data = self._container_infra_client.get(url,
                                                error_message=msg)

        return self._get_and_munchify(key=None, data=data)

    def sign_coe_cluster_certificate(self, cluster_id, csr):
        """Sign client key and generate the CA certificate for a cluster

        :param cluster_id: UUID of the cluster.
        :param csr: Certificate Signing Request (CSR) for authenticating
                    client key.The CSR will be used by Magnum to generate
                    a signed certificate that client will use to communicate
                    with the cluster.

        :returns: a dict representing the signed certs.

        :raises: OpenStackCloudException on operation error.
        """
        error_message = ("Error signing certs for cluster"
                         " {cluster_id}".format(cluster_id=cluster_id))
        with _utils.shade_exceptions(error_message):
            body = {}
            body['cluster_uuid'] = cluster_id
            body['csr'] = csr

            certs = self._container_infra_client.post(
                '/certificates', json=body)

        return self._get_and_munchify(key=None, data=certs)

    @_utils.cache_on_arguments()
    def list_cluster_templates(self, detail=False):
        """List cluster templates.

        :param bool detail. Ignored. Included for backwards compat.
            ClusterTemplates are always returned with full details.

        :returns: a list of dicts containing the cluster template details.

        :raises: ``OpenStackCloudException``: if something goes wrong during
            the OpenStack API call.
        """
        with _utils.shade_exceptions("Error fetching cluster template list"):
            try:
                data = self._container_infra_client.get('/clustertemplates')
                # NOTE(flwang): Magnum adds /clustertemplates and /cluster
                # to deprecate /baymodels and /bay since Newton release. So
                # we're using a small tag to indicate if current
                # cloud has those two new API endpoints.
                self._container_infra_client._has_magnum_after_newton = True
                return self._normalize_cluster_templates(
                    self._get_and_munchify('clustertemplates', data))
            except exc.OpenStackCloudURINotFound:
                data = self._container_infra_client.get('/baymodels/detail')
                return self._normalize_cluster_templates(
                    self._get_and_munchify('baymodels', data))
    list_baymodels = list_cluster_templates
    list_coe_cluster_templates = list_cluster_templates

    def search_cluster_templates(
            self, name_or_id=None, filters=None, detail=False):
        """Search cluster templates.

        :param name_or_id: cluster template name or ID.
        :param filters: a dict containing additional filters to use.
        :param detail: a boolean to control if we need summarized or
            detailed output.

        :returns: a list of dict containing the cluster templates

        :raises: ``OpenStackCloudException``: if something goes wrong during
            the OpenStack API call.
        """
        cluster_templates = self.list_cluster_templates(detail=detail)
        return _utils._filter_list(
            cluster_templates, name_or_id, filters)
    search_baymodels = search_cluster_templates
    search_coe_cluster_templates = search_cluster_templates

    def get_cluster_template(self, name_or_id, filters=None, detail=False):
        """Get a cluster template by name or ID.

        :param name_or_id: Name or ID of the cluster template.
        :param filters:
            A dictionary of meta data to use for further filtering. Elements
            of this dictionary may, themselves, be dictionaries. Example::

                {
                  'last_name': 'Smith',
                  'other': {
                      'gender': 'Female'
                  }
                }

            OR
            A string containing a jmespath expression for further filtering.
            Example:: "[?last_name==`Smith`] | [?other.gender]==`Female`]"

        :returns: A cluster template dict or None if no matching
            cluster template is found.
        """
        return _utils._get_entity(self, 'cluster_template', name_or_id,
                                  filters=filters, detail=detail)
    get_baymodel = get_cluster_template
    get_coe_cluster_template = get_cluster_template

    def create_cluster_template(
            self, name, image_id=None, keypair_id=None, coe=None, **kwargs):
        """Create a cluster template.

        :param string name: Name of the cluster template.
        :param string image_id: Name or ID of the image to use.
        :param string keypair_id: Name or ID of the keypair to use.
        :param string coe: Name of the coe for the cluster template.

        Other arguments will be passed in kwargs.

        :returns: a dict containing the cluster template description

        :raises: ``OpenStackCloudException`` if something goes wrong during
            the OpenStack API call
        """
        error_message = ("Error creating cluster template of name"
                         " {cluster_template_name}".format(
                             cluster_template_name=name))
        with _utils.shade_exceptions(error_message):
            body = kwargs.copy()
            body['name'] = name
            body['image_id'] = image_id
            body['keypair_id'] = keypair_id
            body['coe'] = coe

            try:
                cluster_template = self._container_infra_client.post(
                    '/clustertemplates', json=body)
                self._container_infra_client._has_magnum_after_newton = True
            except exc.OpenStackCloudURINotFound:
                cluster_template = self._container_infra_client.post(
                    '/baymodels', json=body)

        self.list_cluster_templates.invalidate(self)
        return cluster_template
    create_baymodel = create_cluster_template
    create_coe_cluster_template = create_cluster_template

    def delete_cluster_template(self, name_or_id):
        """Delete a cluster template.

        :param name_or_id: Name or unique ID of the cluster template.
        :returns: True if the delete succeeded, False if the
            cluster template was not found.

        :raises: OpenStackCloudException on operation error.
        """

        cluster_template = self.get_cluster_template(name_or_id)

        if not cluster_template:
            self.log.debug(
                "Cluster template %(name_or_id)s does not exist",
                {'name_or_id': name_or_id},
                exc_info=True)
            return False

        with _utils.shade_exceptions("Error in deleting cluster template"):
            if getattr(self._container_infra_client,
                       '_has_magnum_after_newton', False):
                self._container_infra_client.delete(
                    '/clustertemplates/{id}'.format(id=cluster_template['id']))
            else:
                self._container_infra_client.delete(
                    '/baymodels/{id}'.format(id=cluster_template['id']))
            self.list_cluster_templates.invalidate(self)

        return True
    delete_baymodel = delete_cluster_template
    delete_coe_cluster_template = delete_cluster_template

    @_utils.valid_kwargs('name', 'image_id', 'flavor_id', 'master_flavor_id',
                         'keypair_id', 'external_network_id', 'fixed_network',
                         'dns_nameserver', 'docker_volume_size', 'labels',
                         'coe', 'http_proxy', 'https_proxy', 'no_proxy',
                         'network_driver', 'tls_disabled', 'public',
                         'registry_enabled', 'volume_driver')
    def update_cluster_template(self, name_or_id, operation, **kwargs):
        """Update a cluster template.

        :param name_or_id: Name or ID of the cluster template being updated.
        :param operation: Operation to perform - add, remove, replace.

        Other arguments will be passed with kwargs.

        :returns: a dict representing the updated cluster template.

        :raises: OpenStackCloudException on operation error.
        """
        self.list_cluster_templates.invalidate(self)
        cluster_template = self.get_cluster_template(name_or_id)
        if not cluster_template:
            raise exc.OpenStackCloudException(
                "Cluster template %s not found." % name_or_id)

        if operation not in ['add', 'replace', 'remove']:
            raise TypeError(
                "%s operation not in 'add', 'replace', 'remove'" % operation)

        patches = _utils.generate_patches_from_kwargs(operation, **kwargs)
        # No need to fire an API call if there is an empty patch
        if not patches:
            return cluster_template

        with _utils.shade_exceptions(
                "Error updating cluster template {0}".format(name_or_id)):
            if getattr(self._container_infra_client,
                       '_has_magnum_after_newton', False):
                self._container_infra_client.patch(
                    '/clustertemplates/{id}'.format(id=cluster_template['id']),
                    json=patches)
            else:
                self._container_infra_client.patch(
                    '/baymodels/{id}'.format(id=cluster_template['id']),
                    json=patches)

        new_cluster_template = self.get_cluster_template(name_or_id)
        return new_cluster_template
    update_baymodel = update_cluster_template
    update_coe_cluster_template = update_cluster_template

    def list_magnum_services(self):
        """List all Magnum services.
        :returns: a list of dicts containing the service details.

        :raises: OpenStackCloudException on operation error.
        """
        with _utils.shade_exceptions("Error fetching Magnum services list"):
            data = self._container_infra_client.get('/mservices')
            return self._normalize_magnum_services(
                self._get_and_munchify('mservices', data))
