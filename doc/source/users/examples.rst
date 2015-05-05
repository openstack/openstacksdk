OpenStack SDK Examples
======================

An effort has been made to provide some useful examples to try out the
SDK.  These examples reside in the examples directory of the project.
The examples use an authentication configuration that is very similar
to the configuration used for most OpenStack clients.

Configuration
-------------

Most of the examples use a common argument parser to collect
authentication information to run requests.  The authentication may come
from the OS prefixed environment variables similar to the ones used in many
client libraries or you may use
`os-client-config <https://pypi.python.org/pypi/os-client-config>`_.

To use the OS prefixed environment variables, set up something similar to
the following.::

   export OS_REGION_NAME=Manhattan
   export OS_PROJECT_NAME=beasties
   export OS_IDENTITY_API_VERSION=2.0
   export OS_PASSWORD=horovitz
   export OS_AUTH_URL=https://127.0.0.1:5000/v2.0/
   export OS_USERNAME=adrock

To use os-client-config, create a clouds.yaml file, which typically resides in
~/.config/openstack/clouds.yaml to store authentication and preference
information.  If you are using os-client-config, you can use the OS_CLOUD
environment variable or use the --os-cloud command line option to specify
the cloud you want to use.::

   export OS_CLOUD=miked

Running
-------

Once you have a configuration, most examples can be run by calling them
directly.  For example, the list example can be run by just passing it the
name of the resource you want to list::

   python examples/list.py openstack/compute/v2/flavor.py

The example code uses some logic to parse the file name and generate a
resource class name.  That may not work if the resource class name does
not match the file name.  If that is the case, you will need to specify
the resource module name::

   python examples/list.py openstack.network.v2.floating_ip.FloatingIP
