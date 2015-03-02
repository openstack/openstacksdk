:orphan:

Glossary
========

.. glossary::
    :sorted:

    CLI
        Command-Line Interface; a textual user interface.

    compute
        OpenStack Compute (Nova).

    container
        One of the :term:`object-store` resources; a container holds
        :term:`objects <object>` being stored.

    endpoint
        A base URL used in a REST request. An `authentication endpoint` is
        specifically the URL given to a user to identify a cloud. A service
        endpoint is generally obtained from the service catalog.

    host
        A physical computer. Contrast with :term:`node` and :term:`server`.

    identity
        OpenStack Identity (Keystone).

    image
        OpenStack Image (Glance). Also the attribute name of the disk files
        stored for use by servers.

    keypair
        The attribute name of the SSH public key used in the OpenStack Compute
        API for server authentication.

    node
        A logical system, may refer to a :term:`server` (virtual machine) or a
        :term:`host`.

        Generally used to describe an OS instance where a specific process is
        running, e.g. a 'network node' is where the network processes run,
        and may be directly on a host or in a server. Contrast with
        :term:`host` and :term:`server`.

    object
        A generic term which normally refers to the a Python ``object``.
        The OpenStack Object Store service (Swift) also uses `object` as the
        name of the item being stored within a :term:`container`.

    object-store
        OpenStack Object Store (Swift).

    project
        The name of the owner of resources in an OpenStack cloud. A `project`
        can map to a customer, account or organization in different OpenStack
        deployments. Used instead of the deprecated :term:`tenant`.

    region
        The attribute name of a partitioning of cloud resources.

    resource
        A Python object representing an OpenStack resource inside the SDK code.
        Also used to describe the items managed by OpenStack.

    role
        A personality that a user assumes when performing a specific set of
        operations. A `role` includes a set of rights and privileges that a
        user assuming that role inherits. The OpenStack Identity service
        includes the set of roles that a user can assume in the
        :term:`token` that is issued to that user.

        The individual services determine how the roles are interpreted
        and access granted to operations or resources. The OpenStack Identity
        service treats a role as an arbitrary name assigned by the cloud
        administrator.

    server
        A virtual machine or a bare-metal host managed by the OpenStack Compute
        service. Contrast with :term:`host` and :term:`node`.

    service
        In OpenStack this refers to a service/endpoint in the
        :term:`ServiceCatalog <service catalog>`.
        It could also be a collection of endpoints for different
        :term:`regions <region>`.
        A service has a type and a name.

    service catalog
        The list of :term:`services <service>` configured at a given
        authentication endpoint available to the authenticated user.

    tenant
        Deprecated in favor of :term:`project`.

    token
        An arbitrary bit of text that is used to access resources. Some tokens
        are `scoped` to determine what resources are accessible with it. A
        token may be revoked at any time and is valid for a finite duration.

    volume
        OpenStack Volume (Cinder). Also the attribute name of the virtual
        disks managed by the OpenStack Volume service.
