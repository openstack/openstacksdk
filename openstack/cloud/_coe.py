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

from openstack.cloud import _utils
from openstack.cloud import openstackcloud
from openstack import exceptions


class CoeCloudMixin(openstackcloud._OpenStackCloudMixin):
    def list_coe_clusters(self):
        """List COE (Container Orchestration Engine) cluster.

        :returns: A list of container infrastructure management ``Cluster``
            objects.
        :raises: :class:`~openstack.exceptions.SDKException` if something goes
            wrong during the OpenStack API call.
        """
        return list(self.container_infrastructure_management.clusters())

    def search_coe_clusters(self, name_or_id=None, filters=None):
        """Search COE cluster.

        :param name_or_id: cluster name or ID.
        :param filters: a dict containing additional filters to use.
        :param detail: a boolean to control if we need summarized or
            detailed output.

        :returns: A list of container infrastructure management ``Cluster``
            objects.
        :raises: :class:`~openstack.exceptions.SDKException` if something goes
            wrong during the OpenStack API call.
        """
        coe_clusters = self.list_coe_clusters()
        return _utils._filter_list(coe_clusters, name_or_id, filters)

    def get_coe_cluster(self, name_or_id, filters=None):
        """Get a COE cluster by name or ID.

        :param name_or_id: Name or ID of the cluster.
        :param filters:
            A dictionary of meta data to use for further filtering. Elements
            of this dictionary may, themselves, be dictionaries. Example::

                {'last_name': 'Smith', 'other': {'gender': 'Female'}}

            OR
            A string containing a jmespath expression for further filtering.
            Example:: "[?last_name==`Smith`] | [?other.gender]==`Female`]"

        :returns: A container infrastructure management ``Cluster`` object if
            found, else None.
        """
        return _utils._get_entity(self, 'coe_cluster', name_or_id, filters)

    def create_coe_cluster(
        self,
        name,
        cluster_template_id,
        **kwargs,
    ):
        """Create a COE cluster based on given cluster template.

        :param string name: Name of the cluster.
        :param string cluster_template_id: ID of the cluster template to use.
        :param dict kwargs: Any other arguments to pass in.

        :returns: The created container infrastructure management ``Cluster``
            object.
        :raises: :class:`~openstack.exceptions.SDKException` if something goes
            wrong during the OpenStack API call
        """
        cluster = self.container_infrastructure_management.create_cluster(
            name=name,
            cluster_template_id=cluster_template_id,
            **kwargs,
        )

        return cluster

    def delete_coe_cluster(self, name_or_id):
        """Delete a COE cluster.

        :param name_or_id: Name or unique ID of the cluster.

        :returns: True if the delete succeeded, False if the
            cluster was not found.
        :raises: :class:`~openstack.exceptions.SDKException` on operation
            error.
        """

        cluster = self.get_coe_cluster(name_or_id)

        if not cluster:
            self.log.debug(
                "COE Cluster %(name_or_id)s does not exist",
                {'name_or_id': name_or_id},
                exc_info=True,
            )
            return False

        self.container_infrastructure_management.delete_cluster(cluster)
        return True

    def update_coe_cluster(self, name_or_id, **kwargs):
        """Update a COE cluster.

        :param name_or_id: Name or ID of the COE cluster being updated.
        :param kwargs: Cluster attributes to be updated.

        :returns: The updated cluster ``Cluster`` object.

        :raises: :class:`~openstack.exceptions.SDKException` on operation
            error.
        """
        cluster = self.get_coe_cluster(name_or_id)
        if not cluster:
            raise exceptions.SDKException(
                f"COE cluster {name_or_id} not found."
            )

        cluster = self.container_infrastructure_management.update_cluster(
            cluster, **kwargs
        )

        return cluster

    def get_coe_cluster_certificate(self, cluster_id):
        """Get details about the CA certificate for a cluster by name or ID.

        :param cluster_id: ID of the cluster.

        :returns: Details about the CA certificate for the given cluster.
        """
        return (
            self.container_infrastructure_management.get_cluster_certificate(
                cluster_id
            )
        )

    def sign_coe_cluster_certificate(self, cluster_id, csr):
        """Sign client key and generate the CA certificate for a cluster

        :param cluster_id: UUID of the cluster.
        :param csr: Certificate Signing Request (CSR) for authenticating
            client key.The CSR will be used by Magnum to generate a signed
            certificate that client will use to communicate with the cluster.

        :returns: a dict representing the signed certs.
        :raises: :class:`~openstack.exceptions.SDKException` on operation
            error.
        """
        return self.container_infrastructure_management.create_cluster_certificate(  # noqa: E501
            cluster_uuid=cluster_id, csr=csr
        )

    def list_cluster_templates(self, detail=False):
        """List cluster templates.

        :param bool detail. Ignored. Included for backwards compat.
            ClusterTemplates are always returned with full details.

        :returns: a list of dicts containing the cluster template details.
        :raises: :class:`~openstack.exceptions.SDKException` if something goes
            wrong during the OpenStack API call.
        """
        return list(
            self.container_infrastructure_management.cluster_templates()
        )

    def search_cluster_templates(
        self, name_or_id=None, filters=None, detail=False
    ):
        """Search cluster templates.

        :param name_or_id: cluster template name or ID.
        :param filters: a dict containing additional filters to use.
        :param detail: a boolean to control if we need summarized or
            detailed output.

        :returns: a list of dict containing the cluster templates
        :raises: :class:`~openstack.exceptions.SDKException`: if something goes
            wrong during the OpenStack API call.
        """
        cluster_templates = self.list_cluster_templates(detail=detail)
        return _utils._filter_list(cluster_templates, name_or_id, filters)

    def get_cluster_template(self, name_or_id, filters=None, detail=False):
        """Get a cluster template by name or ID.

        :param name_or_id: Name or ID of the cluster template.
        :param filters:
            A dictionary of meta data to use for further filtering. Elements
            of this dictionary may, themselves, be dictionaries. Example::

                {'last_name': 'Smith', 'other': {'gender': 'Female'}}

            OR
            A string containing a jmespath expression for further filtering.
            Example:: "[?last_name==`Smith`] | [?other.gender]==`Female`]"

        :returns: A cluster template dict or None if no matching
            cluster template is found.
        """
        return _utils._get_entity(
            self,
            'cluster_template',
            name_or_id,
            filters=filters,
            detail=detail,
        )

    def create_cluster_template(
        self, name, image_id=None, keypair_id=None, coe=None, **kwargs
    ):
        """Create a cluster template.

        :param string name: Name of the cluster template.
        :param string image_id: Name or ID of the image to use.
        :param string keypair_id: Name or ID of the keypair to use.
        :param string coe: Name of the coe for the cluster template.
            Other arguments will be passed in kwargs.

        :returns: a dict containing the cluster template description
        :raises: :class:`~openstack.exceptions.SDKException` if something goes
            wrong during the OpenStack API call
        """
        cluster_template = (
            self.container_infrastructure_management.create_cluster_template(
                name=name,
                image_id=image_id,
                keypair_id=keypair_id,
                coe=coe,
                **kwargs,
            )
        )

        return cluster_template

    def delete_cluster_template(self, name_or_id):
        """Delete a cluster template.

        :param name_or_id: Name or unique ID of the cluster template.

        :returns: True if the delete succeeded, False if the
            cluster template was not found.
        :raises: :class:`~openstack.exceptions.SDKException` on operation
            error.
        """

        cluster_template = self.get_cluster_template(name_or_id)

        if not cluster_template:
            self.log.debug(
                "Cluster template %(name_or_id)s does not exist",
                {'name_or_id': name_or_id},
                exc_info=True,
            )
            return False

        self.container_infrastructure_management.delete_cluster_template(
            cluster_template
        )
        return True

    def update_cluster_template(self, name_or_id, **kwargs):
        """Update a cluster template.

        :param name_or_id: Name or ID of the cluster template being updated.

        :returns: an update cluster template.
        :raises: :class:`~openstack.exceptions.SDKException` on operation
            error.
        """
        cluster_template = self.get_cluster_template(name_or_id)
        if not cluster_template:
            raise exceptions.SDKException(
                f"Cluster template {name_or_id} not found."
            )

        cluster_template = (
            self.container_infrastructure_management.update_cluster_template(
                cluster_template, **kwargs
            )
        )

        return cluster_template

    def list_magnum_services(self):
        """List all Magnum services.

        :returns: a list of dicts containing the service details.
        :raises: :class:`~openstack.exceptions.SDKException` on operation
            error.
        """
        return list(self.container_infrastructure_management.services())
