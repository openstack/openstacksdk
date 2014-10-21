ServiceFilter
==============
.. automodule:: openstack.auth.service_filter


ServiceFilter object
--------------------

.. autoclass:: openstack.auth.service_filter.ServiceFilter
   :members:

Examples
--------

The ``ServiceFilter`` class can be built with a service type, visibility,
region, name, and version.

Create a service filter
~~~~~~~~~~~~~~~~~~~~~~~

Create a compute service and service preference. Join the services
and match::

    from openstack.auth import service_filter
    from openstack.compute import compute_service
    default = compute_service.ComputeService()
    preference = service_filter.ServiceFilter('compute', version='v2')
    result = preference.join(default)
    matches = (result.match_service_type('compute') and
               result.match_service_name('Hal9000') and
               result.match_region('DiscoveryOne') and
               result.match_visibility('public'))
    print(str(result))
    print("matches=" + str(matches))

The resulting output from the code::

    service_type=compute,visibility=public,version=v2
    matches=True
