# 快速开始

基于 [python-openstacksdk v0.9.16](https://github.com/openstack/python-openstacksdk/tree/0.9.16), 
我们添加了6个新的华为OpenStack服务的SDK，这6个服务为：

- CES
- ELB
- VBS
- AS
- DNS
- MRS

新增的SDK的 `架构`,`设计`, `结构`,`代码` 等都遵循 `python-openstacksdk` 的 `Contribute` 规范。

!> 如果想开发任意的SDK，或者对已有SDK开发有任何疑问，请最优先参阅 [官方的代码贡献规范](https://developer.openstack.org/sdks/python/openstacksdk/contributors/index.html)。 


## 环境准备

1. `python-openstacksdk` 适用于 Python 2.7.x 和 3.5.x 系列版本。你可以通过在命令行中执行如下命令来查看你的python版本：
```shell
python --version
```

2. 要使用`python-openstacksdk`，你需要如下的认证信息，这些认证信息也被称为 `OpenStack RC`，正常可以从管理后台直接下载到。
	- auth url
	- user
	- secret
	- user domain id
	- project id 

!> 如果你对上面的认证所需的信息没有任何头绪，请联系你的OpenStack管理员



## SDK获取和安装

目前你只能通过 `github` 来安装SDK：

```bash
# 从最新 master 分支的代码进行安装
pip install git+git://github.com/Huawei/python-openstacksdk.git
# 从 Master 分支的归档文档安装
pip install https://github.com/Huawei/python-openstacksdk/archive/master.zip
# 从名为 branch 分支的归档文档安装
# pip install https://github.com/Huawei/python-openstacksdk/archive/branch.zip
```

当然你也可以自行下载源码进行安装：

```bash
cd your-workspace-folder
git clone https://github.com/Huawei/python-openstacksdk huawei-python-openstacksdk
cd huawei-python-openstacksdk
# install master
git checkout master
pip install -r requirements.txt
python setup.py install
```
?> `pip` 是一个通用的 Python 包安装工具，您可以在PyPI上的 [pip](https://pypi.python.org/pypi/pip?spm=5176.doc53090.2.5.HvQ4RF) 页面上获取到这个工具的相关信息（包括如何安装使用）。

## 开始使用

!> 请访问 [python-openstacksdk User Guide](https://developer.openstack.org/sdks/python/openstacksdk/users/index.html) 来获取完整的手册和入门使用指南。


**1. 创建到OpenStack的连接**

?> 关于如何创建连接的 [官方文档](https://developer.openstack.org/sdks/python/openstacksdk/users/guides/connect.html)

要使用openstacksdk, 首先你需要一个初始化一个 `Connection` 来连接到 `OpenStack`。openstacksdk 提供了三种方式来创建Connection，分别为使用 `Connection`类, 配置文件 或者 环境变量。假如这是你第一次使用SDK，我们建议你先直接使用`Connection`类来进行创建，这种方式最直观。以下代码展示了创建过程，其中的各个认证参数对应 **环境准备** 那一节中的认证信息。

以德电环境为例：

```python
import os

from openstack import connection

os.environ.setdefault(
    'OS_CLOUD_EYE_ENDPOINT_OVERRIDE',
    'https://ces.eu-de.otc.t-systems.com/V1.0/%(project_id)s'
)

conn = connection.Connection(auth_url="https://iam.eu-de.otc.t-systems.com/v3",
                             project_id="d4f2557d248e4860829f5fef030b209c",
                             user_domain_id="bb42e2cd2b784ac4bdc350fb660a2bdb",
                             username="*********",
                             password="*********")
```

以上代码和官方的初始化有点不一样，多了环境变量的设置，这是在官方的基础上新增的功能。由于部分环境的`Service`和`Endpoint`没有注册到OpenStack的Identify服务中，导致在认证返回的token信息中无法找到对应服务的catalog的定义，这样就没办法使用SDK中的这部分服务了。因此，我们新增了通过环境变量来设置服务的Endpoint的功能，只要在环境变量中找到 `OS_${服务类型}_ENDPOINT_OVERRIDE`的环境变量，那么就会将该变量的值作为该`${服务类型}`的Endpoint。

!> 通过环境变量设置的Endpoint，优先级是最高的，会覆盖其他方式获取到的Endpoint。

**2. 调用SDK来访问服务**

在创建完连接之后，使用`Connection`就可以访问到所有的默认服务的API。以`DNS`SDK的查询Zone列表为例，完整的代码如下：

```python
import os

from openstack import connection

os.environ.setdefault(
    'OS_CLOUD_EYE_ENDPOINT_OVERRIDE',
    'https://ces.eu-de.otc.t-systems.com/V1.0/%(project_id)s'
)

conn = connection.Connection(auth_url="https://iam.eu-de.otc.t-systems.com/v3",
                             project_id="d4f2557d248e4860829f5fef030b209c",
                             user_domain_id="bb42e2cd2b784ac4bdc350fb660a2bdb",
                             username="*********",
                             password="*********")

# 获取所有的Zone列表     
zones = conn.dns.zones(limit=20)
for zone in zones:
    print zone
```


**3. 各个服务SDK的使用方式**

- 官方已经提供部分OpenStack基础服务的SDK，具体的用法请查阅官方文档
- 华为在官方的基础上新增了6个华为云服务的SDK，具体的用法请查阅对应的使用手册
	- [DNS](zh-cn/dns-sdk)
	- [CES](zh-cn/ces-sdk)
	- [AS](zh-cn/as-sdk)
	- [VBS](zh-cn/vbs-sdk)
	- [ELB](zh-cn/elb-sdk)
	- [MRS](zh-cn/mrs-sdk)
	

## 服务映射

| ServiceName |  ServiceType  |                              URL example                             |
|:-----------:|:-------------:|:--------------------------------------------------------------------:|
|     VBS     | volume-backup |         https://vbs.eu-de.otc.t-systems.com/v2/%(project_id)s        |
|     CES     |   cloud-eye   |        https://ces.eu-de.otc.t-systems.com/v1.0/%(project_id)s       |
|      AS     |  auto-scaling | https://as.eu-de.otc.t-systems.com/autoscaling-api/v1/%(project_id)s |
|     ELB     |  load-balance |    https://elb.eu-de.otc.t-systems.com/v1.0/elbaas/%(project_id)s    |
|     DNS     |      dns      |                 https://dns.eu-de.otc.t-systems.com/v2               |
|     MRS     |   map-reduce  |        https://mrs.eu-de.otc.t-systems.com/v1.1/%(project_id)s       |