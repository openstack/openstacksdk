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

=================
Managing Clusters
=================

Clusters are first-class citizens in Senlin service design. A cluster is
defined as a collection of homogeneous objects. The "homogeneous" here means
that the objects managed (aka. Nodes) have to be instantiated from the same
"profile type".


List Clusters
~~~~~~~~~~~~~

To examine the list of receivers:

.. literalinclude:: ../../examples/clustering/cluster.py
   :pyobject: list_cluster

When listing clusters, you can specify the sorting option using the ``sort``
parameter and you can do pagination using the ``limit`` and ``marker``
parameters.

Full example: `manage cluster`_


Create Cluster
~~~~~~~~~~~~~~

When creating a cluster, you will provide a dictionary with keys and values
according to the cluster type referenced.

.. literalinclude:: ../../examples/clustering/cluster.py
   :pyobject: create_cluster

Optionally, you can specify a ``metadata`` keyword argument that contains some
key-value pairs to be associated with the cluster.

Full example: `manage cluster`_


Get Cluster
~~~~~~~~~~~

To get a cluster based on its name or ID:

.. literalinclude:: ../../examples/clustering/cluster.py
   :pyobject: get_cluster

Full example: `manage cluster`_


Find Cluster
~~~~~~~~~~~~

To find a cluster based on its name or ID:

.. literalinclude:: ../../examples/clustering/cluster.py
   :pyobject: find_cluster

Full example: `manage cluster`_


Update Cluster
~~~~~~~~~~~~~~

After a cluster is created, most of its properties are immutable. Still, you
can update a cluster's ``name`` and/or ``params``.

.. literalinclude:: ../../examples/clustering/cluster.py
   :pyobject: update_cluster

Full example: `manage cluster`_


Delete Cluster
~~~~~~~~~~~~~~

A cluster can be deleted after creation, When there are nodes in the cluster,
the Senlin engine will launch a process to delete all nodes from the cluster
and destroy them before deleting the cluster object itself.

.. literalinclude:: ../../examples/clustering/cluster.py
   :pyobject: delete_cluster


Add Nodes to Cluster
~~~~~~~~~~~~~~~~~~~~

Add some existing nodes into the specified cluster.

.. literalinclude:: ../../examples/clustering/cluster.py
   :pyobject: add_nodes_to_cluster


Remove Nodes from Cluster
~~~~~~~~~~~~~~~~~~~~~~~~~

Remove nodes from specified cluster.

.. literalinclude:: ../../examples/clustering/cluster.py
   :pyobject: remove_nodes_from_cluster


Replace Nodes in Cluster
~~~~~~~~~~~~~~~~~~~~~~~~

Replace some existing nodes in the specified cluster.

.. literalinclude:: ../../examples/clustering/cluster.py
   :pyobject: replace_nodes_in_cluster


Cluster Scale Out
~~~~~~~~~~~~~~~~~

Inflate the size of a cluster.

.. literalinclude:: ../../examples/clustering/cluster.py
   :pyobject: scale_out_cluster


Cluster Scale In
~~~~~~~~~~~~~~~~

Shrink the size of a cluster.

.. literalinclude:: ../../examples/clustering/cluster.py
   :pyobject: scale_out_cluster


Cluster Resize
~~~~~~~~~~~~~~

Resize of cluster.

.. literalinclude:: ../../examples/clustering/cluster.py
   :pyobject: resize_cluster


Attach Policy to Cluster
~~~~~~~~~~~~~~~~~~~~~~~~

Once a policy is attached (bound) to a cluster, it will be
enforced when related actions are performed on that cluster,
unless the policy is (temporarily) disabled on the cluster

.. literalinclude:: ../../examples/clustering/cluster.py
   :pyobject: attach_policy_to_cluster


Detach Policy from Cluster
~~~~~~~~~~~~~~~~~~~~~~~~~~

Once a policy is attached to a cluster, it can be detached
from the cluster at user's request.

.. literalinclude:: ../../examples/clustering/cluster.py
   :pyobject: detach_policy_from_cluster


Cluster Check
~~~~~~~~~~~~~

Check cluster health status, Cluster members can be check.

.. literalinclude:: ../../examples/clustering/cluster.py
   :pyobject: check_cluster


Cluster Recover
~~~~~~~~~~~~~~~

To restore a specified cluster, members in the cluster will be checked.

.. literalinclude:: ../../examples/clustering/cluster.py
   :pyobject: recover_cluster


.. _manage cluster: https://opendev.org/openstack/openstacksdk/src/branch/master/examples/clustering/cluster.py

