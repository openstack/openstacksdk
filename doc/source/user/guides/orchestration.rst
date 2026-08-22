Using OpenStack Orchestration
=============================

Before working with the Orchestration service, you'll need to create a
connection to your OpenStack cloud by following the :doc:`connect` user
guide. This will provide you with the ``conn`` variable used in the examples
below.

.. contents:: Table of Contents
   :local:

The Orchestration service creates and manages *stacks* - collections of
resources described by a template - along with the software configurations and
deployments applied to them. The examples below show a representative subset of
what is possible; for the complete set of operations, see the
:doc:`Orchestration proxy reference </user/proxies/orchestration>`.

Working with Stacks
-------------------

To list the existing stacks, use the
:meth:`~openstack.orchestration.v1._proxy.Proxy.stacks` method, which returns a
generator of :class:`~openstack.orchestration.v1.stack.Stack` objects::

    >>> for stack in conn.orchestration.stacks():
    ...     print(stack.name, stack.status)

To create a stack from a template, use the
:meth:`~openstack.orchestration.v1._proxy.Proxy.create_stack` method::

    >>> stack = conn.orchestration.create_stack(
    ...     name='my-stack',
    ...     template_url='https://example.com/template.yaml',
    ...     parameters={'key_name': 'my-key'})

To retrieve, update or delete a stack, use the
:meth:`~openstack.orchestration.v1._proxy.Proxy.get_stack`,
:meth:`~openstack.orchestration.v1._proxy.Proxy.update_stack` and
:meth:`~openstack.orchestration.v1._proxy.Proxy.delete_stack` methods. Each
accepts either a stack ID or a
:class:`~openstack.orchestration.v1.stack.Stack` instance::

    >>> stack = conn.orchestration.get_stack(stack.id)
    >>> conn.orchestration.delete_stack(stack)

You can validate a template before using it with
:meth:`~openstack.orchestration.v1._proxy.Proxy.validate_template`, and inspect
the resources that make up a stack with
:meth:`~openstack.orchestration.v1._proxy.Proxy.resources`.

Software Configurations and Deployments
---------------------------------------

Software configurations and the deployments that apply them to servers are
managed through the corresponding ``create_software_config`` /
``software_configs`` and ``create_software_deployment`` /
``software_deployments`` methods.
