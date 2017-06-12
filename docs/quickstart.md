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

Refer:: the best document:: [official document](https://developer.openstack.org/sdks/python/openstacksdk/users/guides/connect.html)




**2. use libraries**

For libraries provided by official, please refer to the official documentation.
