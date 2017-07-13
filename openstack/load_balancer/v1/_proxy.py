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

from openstack import proxy2
from openstack.load_balancer.v1 import certificate as _cert
from openstack.load_balancer.v1 import load_balancer as _lb
from openstack.load_balancer.v1 import listener as _listener
from openstack.load_balancer.v1 import health_check as _hc
from openstack.load_balancer.v1 import job as _job
from openstack.load_balancer.v1 import quota as _quota


class Proxy(proxy2.BaseProxy):
    def create_load_balancer(self, **attrs):
        """Create a new load balancer from attributes

        :param dict attrs: Keyword arguments which will be used to create
            a :class:`~openstack.load_balancer.v1.load_balancer.LoadBalancer`,
            comprised of the properties on the LoadBalancer class.

        :returns: a asynchronous LoadBalancer job
        :rtype: :class:`~openstack.load_balancer.v1.load_balancer.
                            LoadBalancerJob`
        """
        return self._create(_lb.LoadBalancerJob, prepend_key=False, **attrs)

    def get_load_balancer(self, load_balancer):
        """Get a certificate

        :param load_balancer: Either the ID of a load_balancer or an instance
            of :class:`~openstack.load_balancer.v1.load_balancer.LoadBalancer`
        :returns: One
             :class:`~openstack.load_balancer.v1.load_balancer.LoadBalancer`
        """
        return self._get(_lb.LoadBalancer, load_balancer)

    def update_load_balancer(self, load_balancer, **attrs):
        """Update a server

        :param load_balancer: Either the ID of a load_balancer or an instance
            of :class:`~openstack.load_balancer.v1.load_balancer.LoadBalancer`
        :attrs kwargs: The attributes to update on the load_balancer
                        represented by ``load_balancer``.
        :returns: a asynchronous LoadBalancer job
        :rtype: :class:`~openstack.load_balancer.v1.load_balancer.
                            LoadBalancerJob`
        """
        if isinstance(load_balancer, _lb.LoadBalancer):
            load_balancer = load_balancer.id
        return self._update(_lb.LoadBalancerJob,
                            load_balancer,
                            prepend_key=False,
                            **attrs)

    def load_balancers(self, **query):
        """Retrieve a generator of certificates

         :param dict query: Optional query parameters to be sent to limit the
                      resources being returned.
            * ``id``: load balancer id
            * ``name``: load balancer  name
            * ``status``: load balancer status
            * ``bandwidth``: load balancer bandwidth
            * ``vpc_id``: load balancer vpc_id
            * ``vip_subnet_id``: load balancer vip_subnet_id
            * ``vip_address``: load balancer vip_address
            * ``security_group_id``: load balancer security_group_id
            * ``description``: load balancer description
            * ``is_admin_state_up``: admin state up

        :returns: A generator of config (:class:`~openstack.load_balancer.v1.
                load_balancer.LoadBalancer`) instances
        """
        return self._list(_lb.LoadBalancer, paginated=False, **query)

    def delete_load_balancer(self, load_balancer, ignore_missing=True):
        """Delete a certificate

        :param load_balancer: Either the ID of a load_balancer or an instance
            of :class:`~openstack.load_balancer.v1.load_balancer.LoadBalancer`
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be raised when
            the load balancer does not exist.
            When set to ``True``, no exception will be set when attempting to
            delete a nonexistent load balancer.

        :returns: a asynchronous LoadBalancer job
        :rtype: :class:`~openstack.load_balancer.v1.load_balancer.
                            LoadBalancerJob`
        """
        if isinstance(load_balancer, _lb.LoadBalancer):
            load_balancer = load_balancer.id
        return self._delete(_lb.LoadBalancerJob, load_balancer,
                            has_body=True,
                            ignore_missing=ignore_missing)

    def find_load_balancer(self, name_or_id, ignore_missing=True):
        """Find a single load balancer

        :param name_or_id: The name or ID of a certificate
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be raised
            when the load balancer does not exist.
            When set to ``True``, no exception will be set when attempting
            to delete a nonexistent load balancer.

        :returns: ``None``
        """
        return self._find(_lb.LoadBalancer, name_or_id,
                          ignore_missing=ignore_missing)

    def create_certificate(self, **attrs):
        """Create a new certificate from attributes

        :param dict attrs: Keyword arguments which will be used to create
            a :class:`~openstack.certificate.v1.certificate.Certificate`,
            comprised of the properties on the Certificate class.

        :returns: a certificate instance
        :rtype: :class:`~openstack.certificate.v1.certificate.Certificate`
        """
        return self._create(_cert.Certificate, prepend_key=False, **attrs)

    def update_certificate(self, certificate, **attrs):
        """Update a server

        :param certificate: Either the ID of a certificate or an instance of
                :class:`~openstack.certificate.v1.certificate.Certificate`
        :attrs kwargs: The attributes to update on the certificate represented
                       by ``certificate``.
        :returns: a certificate instance
        :rtype: :class:`~openstack.certificate.v1.certificate.Certificate`
        """
        return self._update(_cert.Certificate,
                            certificate,
                            prepend_key=False,
                            **attrs)

    def certificates(self):
        """Retrieve a generator of certificates

        :returns: A generator of certificate instances
        """
        return self._list(_cert.Certificate, paginated=False)

    def delete_certificate(self, certificate, ignore_missing=True):
        """Delete a certificate

        :param certificate: Either the ID of a certificate or an instance of
                :class:`~openstack.certificate.v1.certificate.Certificate`
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be raised when
            the certificate does not exist.
            When set to ``True``, no exception will be set when attempting to
            delete a nonexistent certificate.

        :returns: a certificate asynchronous job
        :rtype: :class:`~openstack.certificate.v1.certificate.
                            Certificate`
        """
        if isinstance(certificate, _cert.Certificate):
            certificate = certificate.id
        return self._delete(_cert.Certificate, certificate,
                            ignore_missing=ignore_missing)

    def find_certificate(self, name_or_id, ignore_missing=True):
        """Find a single certificate

        :param name_or_id: The name or ID of a certificate
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be raised
            when the certificate does not exist.
            When set to ``True``, no exception will be set when attempting
            to delete a nonexistent certificate.

        :returns: ``None``
        """
        return self._find(_cert.Certificate,
                          name_or_id,
                          ignore_missing=ignore_missing,
                          name=name_or_id)

    def create_listener(self, **attrs):
        """Create a new listener from attributes

        :param dict attrs: Keyword arguments which will be used to create
            a :class:`~openstack.load_balancer.v1.listener.Listener`,
            comprised of the properties on the Listener class.

        :returns: a listener instance
        :rtype: :class:`~openstack.load_balancer.v1.listener.Listener`
        """
        return self._create(_listener.Listener, prepend_key=False, **attrs)

    def get_listener(self, listener):
        """Get a certificate

        :param listener: Either the ID of a listener or an instance of
                :class:`~openstack.load_balancer.v1.listener.Listener`
        :returns: One
             :class:`~openstack.load_balancer.v1.listener.Listener`
        """
        return self._get(_listener.Listener, listener)

    def update_listener(self, listener, **attrs):
        """Update a server

        :param listener: Either the ID of a listener or an instance of
                :class:`~openstack.load_balancer.v1.listener.Listener`
        :attrs kwargs: The attributes to update on the listener represented
                       by ``listener``.
        :returns: a listener instance
        :rtype: :class:`~openstack.load_balancer.v1.listener.
                            Listener`
        """
        return self._update(_listener.Listener,
                            listener,
                            prepend_key=False,
                            **attrs)

    def listeners(self, **query):
        """Retrieve a generator of listeners

        :param dict query: Optional query parameters to be sent to limit the
                      resources being returned.
            * ``id``: load balancer id
            * ``name``: load balancer  name
            * ``status``: load balancer status
            * ``loadbalancer_id``: load balancer id
            * ``healthcheck_id``: healthcheck id
            * ``certificate_id``: certificate id
            * ``port``: port
            * ``protocol``: protocol
            * ``description``: load balancer description
            * ``backend_port``: backend port
            * ``backend_protocol``: backend protocol
            * ``sticky_session_type``:
            * ``lb_algorithm``:
            * ``cookie_timeout``:
            * ``cookie_timeout``:
            * ``tcp_timeout``:
            * ``udp_timeout``:
            * ``ssl_protocols``:
            * ``ssl_ciphers``:

        :returns: A generator of listener instances
        """
        return self._list(_listener.Listener, paginated=False, **query)

    def delete_listener(self, listener, ignore_missing=True):
        """Delete a certificate

        :param listener: Either the ID of a listener or an instance of
                :class:`~openstack.load_balancer.v1.listener.Listener`
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be raised when
            the listener does not exist.
            When set to ``True``, no exception will be set when attempting to
            delete a nonexistent listener.

        :returns: a listener instance
        :rtype: :class:`~openstack.load_balancer.v1.listener.
                            Listener`
        """
        return self._delete(_listener.Listener, listener,
                            ignore_missing=ignore_missing)

    def find_listener(self, name_or_id, ignore_missing=True):
        """Find a single listener

        :param name_or_id: The name or ID of a certificate
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be raised
            when the listener does not exist.
            When set to ``True``, no exception will be set when attempting
            to delete a nonexistent listener.

        :returns: ``None``
        """
        return self._find(_listener.Listener, name_or_id,
                          ignore_missing=ignore_missing,
                          name=name_or_id)

    def create_health_check(self, **attrs):
        """Create a new health check from attributes

        :param dict attrs: Keyword arguments which will be used to create
            a :class:`~openstack.load_balancer.v1.health_check.HealthCheck`,
            comprised of the properties on the HealthCheck class.

        :returns: A health check instance
        :rtype: `:class: ~openstack.load_balancer.v1.health_check.HealthCheck`
        """
        return self._create(_hc.HealthCheck, prepend_key=False, **attrs)

    def get_health_check(self, health_check):
        """Get a health check

        :param health_check: Either the ID of a health check or an instance of
                :class:`~openstack.load_balancer.v1.health_check.HealthCheck`
        :returns: A health check instance
        :rtype: `:class: ~openstack.load_balancer.v1.health_check.HealthCheck`
        """
        return self._get(_hc.HealthCheck, health_check)

    def update_health_check(self, health_check, **attrs):
        """Update a health check

        :param health_check: Either the ID of a health check or an instance of
                :class:`~openstack.load_balancer.v1.health_check.HealthCheck`
        :attrs kwargs: The attributes to update on the health check represented
                       by ``health check``.
        :returns: a health check instance
        :rtype: :class:`~openstack.load_balancer.v1.health check.HealthCheck`
        """
        return self._update(_hc.HealthCheck,
                            health_check,
                            prepend_key=False,
                            **attrs)

    def delete_health_check(self, health_check, ignore_missing=True):
        """Delete a health check

        :param health_check: Either the ID of a health check or an instance of
                :class:`~openstack.load_balancer.v1.health_check.HealthCheck`
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be raised when
            the health check does not exist.
            When set to ``True``, no exception will be set when attempting to
            delete a nonexistent health check.

        :returns: a health check instance
        :rtype: :class:`~openstack.load_balancer.v1.health_check.HealthCheck`
        """
        return self._delete(_hc.HealthCheck, health_check,
                            ignore_missing=ignore_missing)

    def find_health_check(self, name_or_id, ignore_missing=True):
        """Find a single health check

        :param name_or_id: The name or ID of a health check
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be raised
            when the health check does not exist.
            When set to ``True``, no exception will be set when attempting
            to delete a nonexistent health check.

        :returns: health check
        :rtype: :class:`~openstack.load_balancer.v1.health_check.HealthCheck`
        """
        return self._find(_hc.HealthCheck, name_or_id,
                          ignore_missing=ignore_missing,
                          name=name_or_id)

    def add_members_to_listener(self, listener, members):
        """Add backend members for a listener

        :param listener: Either the ID of a listener or an instance of
                :class:`~openstack.load_balancer.v1.listener.Listener`
        :param members: list of dicts which contain the server_id and address.
            server_id is ECS service id, address is ECS server internal IP.
            [{"server_id": "dbecb618-2259-405f-ab17-9b68c4f541b0",
              "address": "172.16.0.31"}] for example.

        :return: a operate member job
        :rtype: :class:`~openstack.load_balancer.v1.listener.OperateMemberJob`
        """
        listener = self._get_resource(_listener.Listener, listener)
        return listener.add_members(self._session, members)

    def remove_members_of_listener(self, listener, members):
        """Remove backend members for a listener

        :param listener: Either the ID of a listener or an instance of
                :class:`~openstack.load_balancer.v1.listener.Listener`
        :param members: member list to be removed from listener,
            list of members (ECS server id) belongs to the listener
            ["dbecb618-2259-405f-ab17-9b68c4f541b0",] for example.

        :return: a operate member job
        :rtype: :class:`~openstack.load_balancer.v1.listener.OperateMemberJob`
        """
        listener = self._get_resource(_listener.Listener, listener)
        return listener.remove_members(self._session, members)

    def listener_members(self, listener, **query):
        """Retrieve a generator of listener members

        :param listener: Either the ID of a listener or an instance of
                :class:`~openstack.load_balancer.v1.listener.Listener`
        :param dict query: Optional query parameters to be sent to limit the
                      resources being returned.
            * ``marker``: pagination marker, member id
            * ``limit``: pagination limit

        :returns: A generator of listener members instances
        """
        listener = self._get_resource(_listener.Listener, listener)
        return self._list(_listener.Member,
                          paginated=True,
                          listener_id=listener.id,
                          **query)

    def get_job(self, job):
        """Get a health check

        :param job: Either the ID of a health check or an instance of
                :class:`~openstack.load_balancer.v1.job.Job`
        :returns: A :class:`~openstack.load_balancer.v1.job.Job`
        """
        return self._get(_job.Job, job)

    def quotas(self):
        """Retrieve a generator of Quota

        :returns: A generator of quota
                (:class:`~openstack.load_balancer.v1.quota.Quota`) instances
        """
        return self._list(_quota.Quota, paginated=False)
