==============
Vendor Support
==============

OpenStack presents deployers with many options, some of which can expose
differences to end users. `os-client-config` tries its best to collect
information about various things a user would need to know. The following
is a text representation of the vendor related defaults `os-client-config`
knows about.

hp
--

https://region-b.geo-1.identity.hpcloudsvc.com:35357/v2.0

============== ================
Region Name    Human Name
============== ================
region-a.geo-1 US West
region-b.geo-1 US East
============== ================

* DNS Service Type is `hpext:dns`
* Image API Version is 1
* Images must be in `qcow2` format
* Floating IPs are provided by Neutron
* Security groups are provided by Neutron

rackspace
---------

https://identity.api.rackspacecloud.com/v2.0/

============== ================
Region Name    Human Name
============== ================
DFW            Dallas
ORD            Chicago
IAD            Washington, D.C.
SYD            Sydney
HKG            Hong Kong
============== ================

* Database Service Type is `rax:database`
* Compute Service Name is `cloudServersOpenStack`
* Image API Version is 2
* Images must be in `vhd` format
* Images must be uploaded using the Glance Task Interface
* Floating IPs are not needed
* Security groups are not supported
* Uploaded Images need properties to not use vendor agent
:vm_mode: hvm
:xenapi_use_agent: False

dreamhost
---------

https://keystone.dream.io/v2.0

============== ================
Region Name    Human Name
============== ================
RegionOne      Region One
============== ================

* Image API Version is 2
* Images must be in `raw` format
* Floating IPs are provided by Neutron
* Security groups are provided by Neutron

vexxhost
--------

http://auth.api.thenebulacloud.com:5000/v2.0/

============== ================
Region Name    Human Name
============== ================
ca-ymq-1       Montreal
============== ================

* Image API Version is 2
* Images must be in `qcow2` format
* Floating IPs are not needed
* Security groups are provided by Neutron

runabove
--------

https://auth.runabove.io/v2.0

============== ================
Region Name    Human Name
============== ================
SBG-1          Strassbourg, FR
BHS-1          Beauharnois, QC
============== ================

* Image API Version is 2
* Images must be in `qcow2` format
* Floating IPs are not needed
* Security groups are provided by Neutron

unitedstack
-----------

https://identity.api.ustack.com/v3

============== ================
Region Name    Human Name
============== ================
bj1            Beijing
gd1            Guangdong
============== ================

* Identity API Version is 3
* Image API Version is 2
* Images must be in `raw` format
* Floating IPs are not needed
* Security groups are provided by Neutron

auro
----

https://api.auro.io:5000/v2.0

============== ================
Region Name    Human Name
============== ================
RegionOne      RegionOne
============== ================

* Identity API Version is 2
* Image API Version is 1
* Images must be in `qcow2` format
* Floating IPs are provided by Nova
* Security groups are provided by Nova
