# HuaWei SDK Client Initial

## 1. credentials

Ask OpenStack environment administrator to get credentials, a credentials should contains infomation below:

- user
- secret
- auth url
- user domain id
- project id 

## 2. connect OpenStack Cloud

- [Connect with python](https://developer.openstack.org/sdks/python/openstacksdk/users/guides/connect.html)
- [Connect From Yaml Config File](https://developer.openstack.org/sdks/python/openstacksdk/users/guides/connect_from_config.html)


## 3. Endpoint mapping

| ServiceName |  ServiceType  |                              URL example                             |
|:-----------:|:-------------:|:--------------------------------------------------------------------:|
|     VBS     | volume-backup |         https://vbs.eu-de.otc.t-systems.com/v2/%(project_id)s        |
|     CES     |   cloud-eye   |        https://ces.eu-de.otc.t-systems.com/v1.0/%(project_id)s       |
|      AS     |  auto-scaling | https://as.eu-de.otc.t-systems.com/autoscaling-api/v1/%(project_id)s |
|     ELB     |  load-balance |    https://elb.eu-de.otc.t-systems.com/v1.0/elbaas/%(project_id)s    |
|     DNS     |      dns      |                 https://dns.eu-de.otc.t-systems.com/v2               |
|     MRS     |   map-reduce  |        https://mrs.eu-de.otc.t-systems.com/v1.1/%(project_id)s       |
