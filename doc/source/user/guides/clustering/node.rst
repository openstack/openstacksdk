..
  Licensed under the Apache License, Version 2.0 (the "License"); you may
  not use this file except in compliance with the License. You may obtain
  a copy of the License at

          http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
  License for the specific language governing permissions and limitations
  under the License.

==============
Managing Nodes
==============

Node is a logical object managed by the Senlin service. A node can be a member
of at most one cluster at any time. A node can be an orphan node which means
it doesn't belong to any clusters.


List Nodes
~~~~~~~~~~

To examine the list of Nodes:

.. literalinclude:: ../../examples/clustering/node.py
   :pyobject: list_nodes

When listing nodes, you can specify the sorting option using the ``sort``
parameter and you can do pagination using the ``limit`` and ``marker``
parameters.

Full example: `manage node`_


Create Node
~~~~~~~~~~~

When creating a node, you will provide a dictionary with keys and values
according to the node type referenced.

.. literalinclude:: ../../examples/clustering/node.py
   :pyobject: create_node

Optionally, you can specify a ``metadata`` keyword argument that contains some
key-value pairs to be associated with the node.

Full example: `manage node`_


Get Node
~~~~~~~~

To get a node based on its name or ID:

.. literalinclude:: ../../examples/clustering/node.py
   :pyobject: get_node

Full example: `manage node`_


Find Node
~~~~~~~~~

To find a node based on its name or ID:

.. literalinclude:: ../../examples/clustering/node.py
   :pyobject: find_node

Full example: `manage node`_


Update Node
~~~~~~~~~~~

After a node is created, most of its properties are immutable. Still, you
can update a node's ``name`` and/or ``params``.

.. literalinclude:: ../../examples/clustering/node.py
   :pyobject: update_node

Full example: `manage node`_


Delete Node
~~~~~~~~~~~

A node can be deleted after creation, provided that it is not referenced
by any active clusters. If you attempt to delete a node that is still in
use, you will get an error message.

.. literalinclude:: ../../examples/clustering/node.py
   :pyobject: delete_node

Full example: `manage node`_


Check Node
~~~~~~~~~~

If the underlying physical resource is not healthy, the node will be set
to ERROR status.

.. literalinclude:: ../../examples/clustering/node.py
   :pyobject: check_node

Full example: `manage node`_


Recover Node
~~~~~~~~~~~~

To restore a specified node.

.. literalinclude:: ../../examples/clustering/node.py
   :pyobject: recover_node

.. _manage node: http://git.openstack.org/cgit/openstack/python-openstacksdk/tree/examples/clustering/node.py
