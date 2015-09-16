==============
Vendor Support
==============

OpenStack presents deployers with many options, some of which can expose
differences to end users. `os-client-config` tries its best to collect
information about various things a user would need to know. The following
is a text representation of the vendor related defaults `os-client-config`
knows about.

Default Values
--------------

These are the default behaviors unless a cloud is configured differently.

* Identity uses `password` authentication
* Identity API Version is 2
* Image API Version is 2
* Images must be in `qcow2` format
* Images are uploaded using PUT interface
* Public IPv4 is directly routable via DHCP from Neutron
* IPv6 is not provided
* Floating IPs are provided by Neutron
* Security groups are provided by Neutron
* Vendor specific agents are not used

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
* Public IPv4 is provided via NAT with Neutron Floating IP

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
* Images must be in `vhd` format
* Images must be uploaded using the Glance Task Interface
* Floating IPs are not needed
* Public IPv4 is directly routable via static config by Nova
* IPv6 is provided to every server
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

* Images must be in `raw` format
* Public IPv4 is provided via NAT with Neutron Floating IP
* IPv6 is provided to every server

vexxhost
--------

http://auth.api.thenebulacloud.com:5000/v2.0/

============== ================
Region Name    Human Name
============== ================
ca-ymq-1       Montreal
============== ================

runabove
--------

https://auth.runabove.io/v2.0

============== ================
Region Name    Human Name
============== ================
SBG-1          Strassbourg, FR
BHS-1          Beauharnois, QC
============== ================

* Floating IPs are not supported

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
* Images must be in `raw` format

auro
----

https://api.auro.io:5000/v2.0

============== ================
Region Name    Human Name
============== ================
van1           Vancouver, BC
============== ================

* Public IPv4 is provided via NAT with Nova Floating IP
* Floating IPs are provided by Nova
* Security groups are provided by Nova

ovh
---

https://auth.cloud.ovh.net/v2.0

============== ================
Region Name    Human Name
============== ================
SBG-1          Strassbourg, FR
GRA-1          Gravelines, FR
============== ================

* Images must be in `raw` format
* Floating IPs are not supported

citycloud
---------

https://identity1.citycloud.com:5000/v3/

============== ================
Region Name    Human Name
============== ================
Lon1           London, UK
Sto2           Stockholm, SE
Kna1           Karlskrona, SE
============== ================

* Identity API Version is 3
* Public IPv4 is provided via NAT with Neutron Floating IP

elastx
------

https://ops.elastx.net:5000/v2.0

============== ================
Region Name    Human Name
============== ================
regionOne      Region One
============== ================

* Public IPv4 is provided via NAT with Neutron Floating IP

entercloudsuite
---------------

https://api.entercloudsuite.com/v2.0

============== ================
Region Name    Human Name
============== ================
nl-ams1        Amsterdam, NL
it-mil1        Milan, IT
de-fra1        Frankfurt, DE
============== ================

ultimum
-------

https://console.ultimum-cloud.com:5000/v2.0

============== ================
Region Name    Human Name
============== ================
RegionOne      Region One
============== ================

datacentred
-----------

https://compute.datacentred.io:5000/v2.0

============== ================
Region Name    Human Name
============== ================
sal01          Manchester, UK
============== ================

* Image API Version is 1

internap
--------

https://identity.api.cloud.iweb.com/v2.0

============== ================
Region Name    Human Name
============== ================
ams01          Amsterdam, NL
da01           Dallas, TX
nyj01          New York, NY
============== ================

* Image API Version is 1
* Floating IPs are not supported
