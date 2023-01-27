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

from openstack.container_infrastructure_management.v1 import (
    cluster as _cluster
)
from openstack.container_infrastructure_management.v1 import (
    cluster_certificate as _cluster_cert
)
from openstack.container_infrastructure_management.v1 import (
    cluster_template as _cluster_template
)
from openstack.container_infrastructure_management.v1 import (
    service as _service
)
from openstack import proxy


class Proxy(proxy.Proxy):

    _resource_registry = {
        "cluster": _cluster.Cluster,
        "cluster_template": _cluster_template.ClusterTemplate,
        "service": _service.Service
    }

    def create_cluster(self, **attrs):
        """Create a new cluster from attributes

        :param dict attrs: Keyword arguments which will be used to create a
            :class:`~openstack.container_infrastructure_management.v1.cluster.Cluster`,
            comprised of the properties on the Cluster class.
        :returns: The results of cluster creation
        :rtype:
            :class:`~openstack.container_infrastructure_management.v1.cluster.Cluster`
        """
        return self._create(_cluster.Cluster, **attrs)

    def delete_cluster(self, cluster, ignore_missing=True):
        """Delete a cluster

        :param cluster: The value can be either the ID of a cluster or a
            :class:`~openstack.container_infrastructure_management.v1.cluster.Cluster`
            instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be raised when
            the cluster does not exist. When set to ``True``, no exception will
            be set when attempting to delete a nonexistent cluster.
        :returns: ``None``
        """
        self._delete(_cluster.Cluster, cluster, ignore_missing=ignore_missing)

    def find_cluster(self, name_or_id, ignore_missing=True):
        """Find a single cluster

        :param name_or_id: The name or ID of a cluster.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be
            raised when the resource does not exist.
            When set to ``True``, None will be returned when
            attempting to find a nonexistent resource.
        :returns: One
            :class:`~openstack.container_infrastructure_management.v1.cluster.Cluster`
            or None
        """
        return self._find(
            _cluster.Cluster,
            name_or_id,
            ignore_missing=ignore_missing,
        )

    def get_cluster(self, cluster):
        """Get a single cluster

        :param cluster: The value can be the ID of a cluster or a
            :class:`~openstack.container_infrastructure_management.v1.cluster.Cluster`
            instance.

        :returns: One
            :class:`~openstack.container_infrastructure_management.v1.cluster.Cluster`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
            when no resource can be found.
        """
        return self._get(_cluster.Cluster, cluster)

    def clusters(self, **query):
        """Return a generator of clusters

        :param kwargs query: Optional query parameters to be sent to limit
            the resources being returned.

        :returns: A generator of cluster objects
        :rtype:
            :class:`~openstack.container_infrastructure_management.v1.cluster.Cluster`
        """
        return self._list(_cluster.Cluster, **query)

    def update_cluster(self, cluster, **attrs):
        """Update a cluster

        :param cluster: Either the id of a cluster or a
            :class:`~openstack.container_infrastructure_management.v1.cluster.Cluster`
            instance.
        :param attrs: The attributes to update on the cluster represented
            by ``cluster``.

        :returns: The updated cluster
        :rtype:
            :class:`~openstack.container_infrastructure_management.v1.cluster.Cluster`
        """
        return self._update(_cluster.Cluster, cluster, **attrs)

    # ============== Cluster Templates ==============
    def create_cluster_template(self, **attrs):
        """Create a new cluster_template from attributes

        :param dict attrs: Keyword arguments which will be used to create a
            :class:`~openstack.container_infrastructure_management.v1.cluster_template.ClusterTemplate`,
            comprised of the properties on the ClusterTemplate class.
        :returns: The results of cluster_template creation
        :rtype:
            :class:`~openstack.container_infrastructure_management.v1.cluster_template.ClusterTemplate`
        """
        return self._create(_cluster_template.ClusterTemplate, **attrs)

    def delete_cluster_template(self, cluster_template, ignore_missing=True):
        """Delete a cluster_template

        :param cluster_template: The value can be either the ID of a
            cluster_template or a
            :class:`~openstack.container_infrastructure_management.v1.cluster_template.ClusterTemplate`
            instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be raised when
            the cluster_template does not exist. When set to ``True``, no
            exception will be set when attempting to delete a nonexistent
            cluster_template.
        :returns: ``None``
        """
        self._delete(
            _cluster_template.ClusterTemplate,
            cluster_template,
            ignore_missing=ignore_missing,
        )

    def find_cluster_template(self, name_or_id, ignore_missing=True):
        """Find a single cluster_template

        :param name_or_id: The name or ID of a cluster_template.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be
            raised when the resource does not exist.
            When set to ``True``, None will be returned when
            attempting to find a nonexistent resource.
        :returns: One
            :class:`~openstack.container_infrastructure_management.v1.cluster_template.ClusterTemplate`
            or None
        """
        return self._find(
            _cluster_template.ClusterTemplate,
            name_or_id,
            ignore_missing=ignore_missing,
        )

    def get_cluster_template(self, cluster_template):
        """Get a single cluster_template

        :param cluster_template: The value can be the ID of a cluster_template
            or a
            :class:`~openstack.container_infrastructure_management.v1.cluster_template.ClusterTemplate`
            instance.

        :returns: One
            :class:`~openstack.container_infrastructure_management.v1.cluster_template.ClusterTemplate`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
            when no resource can be found.
        """
        return self._get(_cluster_template.ClusterTemplate, cluster_template)

    def cluster_templates(self, **query):
        """Return a generator of cluster_templates

        :param kwargs query: Optional query parameters to be sent to limit
            the resources being returned.

        :returns: A generator of cluster_template objects
        :rtype:
            :class:`~openstack.container_infrastructure_management.v1.cluster_template.ClusterTemplate`
        """
        return self._list(_cluster_template.ClusterTemplate, **query)

    def update_cluster_template(self, cluster_template, **attrs):
        """Update a cluster_template

        :param cluster_template: Either the id of a cluster_template or a
            :class:`~openstack.container_infrastructure_management.v1.cluster_template.ClusterTemplate`
            instance.
        :param attrs: The attributes to update on the cluster_template
            represented by ``cluster_template``.

        :returns: The updated cluster_template
        :rtype:
            :class:`~openstack.container_infrastructure_management.v1.cluster_template.ClusterTemplate`
        """
        return self._update(
            _cluster_template.ClusterTemplate, cluster_template, **attrs
        )

    # ============== Cluster Certificates ==============
    def create_cluster_certificate(self, **attrs):
        """Create a new cluster_certificate from CSR

        :param dict attrs: Keyword arguments which will be used to create a
            :class:`~openstack.container_infrastructure_management.v1.cluster_certificate.ClusterCertificate`,
            comprised of the properties on the ClusterCertificate class.
        :returns: The results of cluster_certificate creation
        :rtype:
            :class:`~openstack.container_infrastructure_management.v1.cluster_certificate.ClusterCertificate`
        """
        return self._create(_cluster_cert.ClusterCertificate, **attrs)

    def get_cluster_certificate(self, cluster_certificate):
        """Get a single cluster_certificate

        :param cluster_certificate: The value can be the ID of a
            cluster_certificate or a
            :class:`~openstack.container_infrastructure_management.v1.cluster_certificate.ClusterCertificate`
            instance.

        :returns: One
            :class:`~openstack.container_infrastructure_management.v1.cluster_certificate.ClusterCertificate`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
            when no resource can be found.
        """
        return self._get(_cluster_cert.ClusterCertificate, cluster_certificate)

    # ============== Services ==============
    def services(self):
        """Return a generator of services

        :returns: A generator of service objects
        :rtype:
            :class:`~openstack.container_infrastructure_management.v1.service.Service`
        """
        return self._list(_service.Service)
