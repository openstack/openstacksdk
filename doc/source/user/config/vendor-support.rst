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
* Volume API Version is 2
* Compute API Version is 2.1
* Images must be in `qcow2` format
* Images are uploaded using PUT interface
* Public IPv4 is directly routable via DHCP from Neutron
* IPv6 is not provided
* Floating IPs are not required
* Floating IPs are provided by Neutron
* Security groups are provided by Neutron
* Vendor specific agents are not used

AURO
----

https://api.auro.io:5000/v2.0

============== ================
Region Name    Location
============== ================
van1           Vancouver, BC
============== ================

* Public IPv4 is provided via NAT with Neutron Floating IP

Betacloud
---------

https://api-1.betacloud.de:5000

============== ==================
Region Name    Location
============== ==================
betacloud-1    Karlsruhe, Germany
============== ==================

* Identity API Version is 3
* Images must be in `raw` format
* Public IPv4 is provided via NAT with Neutron Floating IP
* Volume API Version is 3

Catalyst
--------

https://api.cloud.catalyst.net.nz:5000/v2.0

============== ================
Region Name    Location
============== ================
nz-por-1       Porirua, NZ
nz_wlg_2       Wellington, NZ
============== ================

* Identity API Version is 3
* Compute API Version is 2
* Images must be in `raw` format
* Volume API Version is 3

City Cloud
----------

https://%(region_name)s.citycloud.com:5000/v3/

============== ================
Region Name    Location
============== ================
Buf1           Buffalo, NY
dx1            Dubai, UAE
Fra1           Frankfurt, DE
Kna1           Karlskrona, SE
Lon1           London, UK
Sto2           Stockholm, SE
tky1           Tokyo, JP
============== ================

* Identity API Version is 3
* Public IPv4 is provided via NAT with Neutron Floating IP
* Volume API Version is 1

ConoHa
------

https://identity.%(region_name)s.conoha.io

============== ================
Region Name    Location
============== ================
tyo1           Tokyo, JP
sin1           Singapore
sjc1           San Jose, CA
============== ================

* Image upload is not supported

DreamCompute
------------

https://iad2.dream.io:5000

============== ================
Region Name    Location
============== ================
RegionOne      Ashburn, VA
============== ================

* Identity API Version is 3
* Images must be in `raw` format
* IPv6 is provided to every server

Open Telekom Cloud
------------------

https://iam.%(region_name)s.otc.t-systems.com/v3

============== ================
Region Name    Location
============== ================
eu-de          Germany
============== ================

* Identity API Version is 3
* Images must be in `vhd` format
* Public IPv4 is provided via NAT with Neutron Floating IP

ELASTX
------

https://ops.elastx.cloud:5000/v3

============== ================
Region Name    Location
============== ================
se-sto         Stockholm, SE
============== ================

* Identity API Version is 3
* Public IPv4 is provided via NAT with Neutron Floating IP

Enter Cloud Suite
-----------------

https://api.entercloudsuite.com/v2.0

============== ================
Region Name    Location
============== ================
nl-ams1        Amsterdam, NL
it-mil1        Milan, IT
de-fra1        Frankfurt, DE
============== ================

* Compute API Version is 2

Fuga
----

https://identity.api.fuga.io:5000

============== ================
Region Name    Location
============== ================
cystack        Netherlands
============== ================

* Identity API Version is 3
* Volume API Version is 3

Internap
--------

https://identity.api.cloud.iweb.com/v2.0

============== ================
Region Name    Location
============== ================
ams01          Amsterdam, NL
da01           Dallas, TX
nyj01          New York, NY
sin01          Singapore
sjc01          San Jose, CA
============== ================

* Floating IPs are not supported

Limestone Networks
------------------

https://auth.cloud.lstn.net:5000/v3

============== ==================
Region Name    Location
============== ==================
us-dfw-1       Dallas, TX
us-slc         Salt Lake City, UT
============== ==================

* Identity API Version is 3
* Images must be in `raw` format
* IPv6 is provided to every server connected to the `Public Internet` network

OVH
---

https://auth.cloud.ovh.net/v3

============== ================
Region Name    Location
============== ================
BHS1           Beauharnois, QC
SBG1           Strassbourg, FR
GRA1           Gravelines, FR
============== ================

* Images may be in `raw` format. The `qcow2` default is also supported
* Floating IPs are not supported

Rackspace
---------

https://identity.api.rackspacecloud.com/v2.0/

============== ================
Region Name    Location
============== ================
DFW            Dallas, TX
HKG            Hong Kong
IAD            Washington, D.C.
LON            London, UK
ORD            Chicago, IL
SYD            Sydney, NSW
============== ================

* Database Service Type is `rax:database`
* Compute Service Name is `cloudServersOpenStack`
* Images must be in `vhd` format
* Images must be uploaded using the Glance Task Interface
* Floating IPs are not supported
* Public IPv4 is directly routable via static config by Nova
* IPv6 is provided to every server
* Security groups are not supported
* Uploaded Images need properties to not use vendor agent::
  :vm_mode: hvm
  :xenapi_use_agent: False
* Block Storage API Version is 2
* The Block Storage API supports version 2 but only version 1 is in
  the catalog. The Block Storage endpoint is
  https://{region_name}.blockstorage.api.rackspacecloud.com/v2/{project_id}
* While passwords are recommended for use, API keys do work as well.
  The `rackspaceauth` python package must be installed, and then the following
  can be added to clouds.yaml::

    auth:
      username: myusername
      api_key: myapikey
    auth_type: rackspace_apikey

SWITCHengines
-------------

https://keystone.cloud.switch.ch:5000/v3

============== ================
Region Name    Location
============== ================
LS             Lausanne, CH
ZH             Zurich, CH
============== ================

* Identity API Version is 3
* Compute API Version is 2
* Images must be in `raw` format
* Volume API Version is 3

Ultimum
-------

https://console.ultimum-cloud.com:5000/v2.0

============== ================
Region Name    Location
============== ================
RegionOne      Prague, CZ
============== ================

* Volume API Version is 1

UnitedStack
-----------

https://identity.api.ustack.com/v3

============== ================
Region Name    Location
============== ================
bj1            Beijing, CN
gd1            Guangdong, CN
============== ================

* Identity API Version is 3
* Images must be in `raw` format
* Volume API Version is 1

VEXXHOST
--------

http://auth.vexxhost.net

============== ================
Region Name    Location
============== ================
ca-ymq-1       Montreal, QC
sjc1           Santa Clara, CA
============== ================

* DNS API Version is 1
* Identity API Version is 3
* Volume API Version is 3

Zetta
-----

https://identity.api.zetta.io/v3

============== ================
Region Name    Location
============== ================
no-osl1        Oslo, NO
============== ================

* DNS API Version is 2
* Identity API Version is 3
