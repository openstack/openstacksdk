# Quick start

Base on [python-openstacksdk v0.9.16](https://github.com/openstack/python-openstacksdk/tree/0.9.16), 
we add six more libraries for HuaWei.Tld OpenStack Services:

- CES
- ELB
- VBS
- AS
- DNS
- MRS

All new added libraries are simulating the implementation of existing `architecture`/`design`/`conventions`. Please refer to the [offcial contributing document](https://developer.openstack.org/sdks/python/openstacksdk/contributors/index.html) when you have any questions with the implementation details.


## Installation

install sdk libraries from github

```bash
cd your-workspace-folder
git clone https://github.com/Huawei/python-openstacksdk huawei-python-openstacksdk
cd huawei-python-openstacksdk
# install master
git checkout master
pip install -r requirements.txt
python setup.py install
```

or

```bash
# install master
pip install https://github.com/Huawei/python-openstacksdk/archive/master.zip
# install branch
# pip install https://github.com/Huawei/python-openstacksdk/archive/branch.zip
```

## usage

> Important:: Visit [python-openstacksdk User Guide](https://developer.openstack.org/sdks/python/openstacksdk/users/index.html) for the full manual and getting started guides.

**1. Connect to an OpenStack Cloud**

- Refer:: the best document:: [official document](https://developer.openstack.org/sdks/python/openstacksdk/users/guides/connect.html)

- New Feature::

In case of services endpoint is not register in some test OpenStack env, `endpoint override` feature is provided. Basiclly, libraries will try to read envirment value `OS_{SERVICE_TYPE}_ENDPOINT_OVERRIDE`, if the value is setted, then the endpoint of `{SERVICE_TYPE}` will be replaced by the envirment value globaly.

For example, codes below will force volume service library use endpoint `https://evs2.eu-de.otc.t-systems.com/v2/%(project_id)s` instead of the endpoint detected from `/v3/auth/token`'s catalog part.

```python
import os
os.environ.setdefault('OS_VOLUME_ENDPOINT_OVERRIDE',
                      'https://evs2.eu-de.otc.t-systems.com/v2/%(project_id)s')

conn = connection.Connection(auth_url="http://openstack:5000/v3",
                                project_name="big_project",
                                username="SDK_user",
                                password="Super5ecretPassw0rd")
```


**2. use libraries**

- For libraries provided by official, please refer to the official documentation.
- For new added libraries::
	- [VBS](vbs-sdk)
	- [CES](ces-sdk)
	- [AS](as-sdk)
	- [DNS](dns-sdk)
	- [ELB](elb-sdk)
	- [MRS](mrs-sdk)

## 3. Endpoint mapping

| ServiceName |  ServiceType  |                              URL example                             |
|:-----------:|:-------------:|:--------------------------------------------------------------------:|
|     VBS     | volume-backup |         https://vbs.eu-de.otc.t-systems.com/v2/%(project_id)s        |
|     CES     |   cloud-eye   |        https://ces.eu-de.otc.t-systems.com/v1.0/%(project_id)s       |
|      AS     |  auto-scaling | https://as.eu-de.otc.t-systems.com/autoscaling-api/v1/%(project_id)s |
|     ELB     |  load-balance |    https://elb.eu-de.otc.t-systems.com/v1.0/elbaas/%(project_id)s    |
|     DNS     |      dns      |                 https://dns.eu-de.otc.t-systems.com/v2               |
|     MRS     |   map-reduce  |        https://mrs.eu-de.otc.t-systems.com/v1.1/%(project_id)s       |