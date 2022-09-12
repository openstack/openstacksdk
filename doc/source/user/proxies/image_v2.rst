Image API v2
============

For details on how to use image, see :doc:`/user/guides/image`

.. automodule:: openstack.image.v2._proxy

The Image v2 Class
------------------

The image high-level interface is available through the ``image`` member of a
:class:`~openstack.connection.Connection` object.  The ``image`` member will
only be added if the service is detected.

Image Operations
^^^^^^^^^^^^^^^^

.. autoclass:: openstack.image.v2._proxy.Proxy
  :noindex:
  :members: create_image, import_image, upload_image, download_image,
            update_image, delete_image, get_image, find_image, images,
            deactivate_image, reactivate_image, stage_image,
            add_tag, remove_tag

Member Operations
^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.image.v2._proxy.Proxy
  :noindex:
  :members: add_member, remove_member, update_member, get_member, find_member,
            members

Task Operations
^^^^^^^^^^^^^^^

.. autoclass:: openstack.image.v2._proxy.Proxy
  :noindex:
  :members: tasks, create_task, get_task, wait_for_task

Schema Operations
^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.image.v2._proxy.Proxy
  :noindex:
  :members: get_images_schema, get_image_schema, get_members_schema,
            get_member_schema, get_tasks_schema, get_task_schema,
            get_metadef_namespace_schema, get_metadef_namespaces_schema,
            get_metadef_resource_type_schema, get_metadef_resource_types_schema,
            get_metadef_object_schema, get_metadef_objects_schema,
            get_metadef_property_schema, get_metadef_properties_schema,
            get_metadef_tag_schema, get_metadef_tags_schema

Service Info Discovery Operations
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.image.v2._proxy.Proxy
  :noindex:
  :members: stores, get_import_info


Metadef Namespace Operations
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.image.v2._proxy.Proxy
  :noindex:
  :members: create_metadef_namespace, delete_metadef_namespace,
            get_metadef_namespace, metadef_namespaces, update_metadef_namespace

Helpers
^^^^^^^

.. autoclass:: openstack.image.v2._proxy.Proxy
   :noindex:
   :members: wait_for_delete
