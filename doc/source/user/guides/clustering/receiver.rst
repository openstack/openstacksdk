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

==================
Managing Receivers
==================

Receivers are the event sinks associated to senlin clusters. When certain
events (or alarms) are seen by a monitoring software, the software can
notify the senlin clusters of those events (or alarms). When senlin receives
those notifications, it can automatically trigger some predefined operations
with preset parameter values.


List Receivers
~~~~~~~~~~~~~~

To examine the list of receivers:

.. literalinclude:: ../../examples/clustering/receiver.py
   :pyobject: list_receivers

When listing receivers, you can specify the sorting option using the ``sort``
parameter and you can do pagination using the ``limit`` and ``marker``
parameters.

Full example: `manage receiver`_


Create Receiver
~~~~~~~~~~~~~~~

When creating a receiver, you will provide a dictionary with keys and values
according to the receiver type referenced.

.. literalinclude:: ../../examples/clustering/receiver.py
   :pyobject: create_receiver

Optionally, you can specify a ``metadata`` keyword argument that contains some
key-value pairs to be associated with the receiver.

Full example: `manage receiver`_


Get Receiver
~~~~~~~~~~~~

To get a receiver based on its name or ID:

.. literalinclude:: ../../examples/clustering/receiver.py
   :pyobject: get_receiver

Full example: `manage receiver`_


Find Receiver
~~~~~~~~~~~~~

To find a receiver based on its name or ID:

.. literalinclude:: ../../examples/clustering/receiver.py
   :pyobject: find_receiver

Full example: `manage receiver`_


Update Receiver
~~~~~~~~~~~~~~~

After a receiver is created, most of its properties are immutable. Still, you
can update a receiver's ``name`` and/or ``params``.

.. literalinclude:: ../../examples/clustering/receiver.py
   :pyobject: update_receiver

Full example: `manage receiver`_


Delete Receiver
~~~~~~~~~~~~~~~

A receiver can be deleted after creation, provided that it is not referenced
by any active clusters. If you attempt to delete a receiver that is still in
use, you will get an error message.

.. literalinclude:: ../../examples/clustering/receiver.py
   :pyobject: delete_receiver


.. _manage receiver: http://git.openstack.org/cgit/openstack/python-openstacksdk/tree/examples/clustering/receiver.py
