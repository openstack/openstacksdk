# AutoScalingService SDK

HuaWei OpenStack `AutoScaling` service SDK
- service entry: `conn.auto_scaling`
- service type: `auto-scaling`


## Group

### List Group

```python
query = {
    "name": "any-as-group-name",
    "status": "INSERVICE",        # INSERVICE，PAUSED，ERROR
    "scaling_configuration_id": "as-config-id",
    "marker": 0,
    "limit": 20
}
groups = conn.auto_scaling.groups(**query)
for group in groups:
    logging.info(group)
```

### Get Group

```python
group = conn.auto_scaling.get_group("any-exists-group-id")
```

> or

```python
group = conn.auto_scaling.get_group(Group(id="any-exists-group-id"))
```


### Create Group

```python
_group = {
  "name": "GroupNameTest",
  "scaling_configuration_id": "any-as-config-id",
  "desire_instance_number": 10,
  "min_instance_number": 2,
  "max_instance_number": 20,
  "cool_down_time": 200,
  "health_periodic_audit_method": "NOVA_AUDIT",
  "health_periodic_audit_time": "5",
  "instance_terminate_policy": "OLD_CONFIG_OLD_INSTANCE",
  "vpc_id": "a8327883-6b07-4497-9c61-68d03ee193a",         # known as router
  "networks": [{                                           # known as network
    "id": "3cd35bca-5a10-416f-8994-f79169559870"
  }],
  "notifications": ["EMAIL"],
  "security_groups": [{
    "id": "23b7b999-0a30-4b48-ae8f-ee201a88a6ab"
  }]
}

group = conn.auto_scaling.create_group(**_group)
logging.info(group.id)
```

### Update Group

```python
_group = {
    "name": "group_name",
    "scaling_configuration_id": "f8327883-6a07-4497-9a61-68c03e8e72a2",
    "desire_instance_number": 1,
    "min_instance_number": 1,
    "max_instance_number": 3,
    "cool_down_time": 200
}

to_update_group_id = "group-id"
group = conn.auto_scaling.update_group(to_update_group_id, **_group)
group = conn.auto_scaling.get_group(group)
logging.info(group)
```

### Delete Group

```python
conn.auto_scaling.delete_group("any-exists-group-id")
```

> or

```python
conn.auto_scaling.delete_group(Group(id="any-exists-group-id"))
```


### Resume Group

```python
conn.auto_scaling.resume_group("any-exists-group-id")
```

> or

```python
conn.auto_scaling.resume_group(Group(id="any-exists-group-id"))
```


### Pause Group

```python
conn.auto_scaling.pause_group("any-exists-group-id")
```

> or

```python
conn.auto_scaling.pause_group(Group(id="any-exists-group-id"))
```



## Config

### List Config

```python
query = {
    "name": "as_config_name",
    "image_id": "image-ref-id",
    "marker": 0,
    "limit": 20
}
configs = conn.auto_scaling.configs(**query)
for config in configs:
    logging.info(config)
```

### Get Config
> Most of get resource function support both ``plain`` ID or resource ``Instance`` with id parameter
```python
config = conn.auto_scaling.get_config("any-exists-config-id")
```

> or

```python
config = conn.auto_scaling.get_config(Config(id="any-exists-config-id"))
```

### Create Config
```python
instance_config = {
    "flavor_id": "103",
    "image_id": "627a1223-2ca3-46a7-8d5f-7aef22c74ee6",
    "disk": [{
        "size": 40,
        "volume_type": "SATA",
        "disk_type": "SYS"
    }],
    "personality": [{
        "path": "/etc/profile.d/authentication.sh",
        "content": "some-base64-text-content"
    }, {
        "path": "/etc/profile.d/env.sh",
        "content": "some-base64-text-content"
    }],
    "metadata": {
        "key1": "value1",
        "tag": "app"
    },
    "key_name": "100vm_key"
}

config_name = "auto-scaling-config-name"
coinfig = conn.auto_scaling.create_config(config_name, **instance_config)
logging.info(config.id)
```

### Delete Config
```python
conn.auto_scaling.delete_config(Config(id="any-exists-config-id"))
```
> or
```python
conn.auto_scaling.delete_config("any-exists-config-id")
```


### Batch Delete Configs
- `configs`: Config list, the list item value can be the ID of a config or
    a class:`openstack.auto_scaling.v2.config.Config` instance.
```python
configs = [
    "config-id-1",
    "config-id-2",
    _config.Config(id="config-id-3")
]
conn.auto_scaling.batch_delete_configs(configs)
```


## Policy

### List Policy

```python
query = {
    "scaling_group_id": "any-group-id",
    "name": "as_policy_name",
    "type": "ALARM",                # ALARM, SCHEDULED, RECURRENCE
    "marker": 0,
    "limit": 20
}
policies = conn.auto_scaling.policies(**query)
for policy in policies:
    logging.info(policy)
```

### Get Policy
> Most of get resource function support both ``plain`` ID or resource ``Instance`` with id parameter

```python
policies = conn.auto_scaling.get_policy("any-exists-policy-id")
```

> or

```python
policies = conn.auto_scaling.get_policy(Policy(id="any-exists-policy-id"))
```

### Create Policy
```python
as_group_id = "as-group-id"
as_policy_name = "as-policy-name"
_policy = {
    "name": as_policy_name,
    "scaling_policy_action": {
        "operation": "ADD",
        "instance_number": 1
    },
    "cool_down_time": 900,
    "scheduled_policy": {
        "launch_time": "16:00",
        "recurrence_type": "Daily",
        "recurrence_value": None,
        "start_time": "2017-07-14T03:34Z",
        "end_time": "2017-07-27T03:34Z"
    },
    "type": "RECURRENCE",
    "scaling_group_id": as_group_id
}

policy = conn.auto_scaling.create_policy(**_policy)
policy = conn.auto_scaling.get_policy(policy)
logging.info(policy)
```

### Update Policy
```python
new_policy_name = "as-policy-name"
_policy = {
    "name": "policy_01",
    "type": "RECURRENCE",
    "scheduled_policy": {
        "launch_time": "16:00",
        "recurrence_type": "Daily",
        "recurrence_value": None,
        "end_time": "2016-02-08T17:31Z",
        "start_time": "2016-01-08T17:31Z"
    },
    "scaling_policy_action": {
        "operation": "SET",
        "instance_number": 2
    },
    "cool_down_time": 300
}

to_update_policy_id = "as-policy-id"
policy = conn.auto_scaling.update_policy(to_update_policy_id, **_policy)
policy = conn.auto_scaling.get_policy(policy)
logging.info(policy)
```

### Delete Policy
```python
conn.auto_scaling.delete_policy(Policy(id="any-exists-policy-id"))
```
> or
```python
conn.auto_scaling.delete_policy("any-exists-policy-id")
```

### Execute Policy
```python
conn.auto_scaling.execute_policy(Policy(id="any-exists-policy-id"))
```
> or

```python
conn.auto_scaling.execute_policy("any-exists-policy-id")
```

### Resume Policy
```python
conn.auto_scaling.resume_policy(Policy(id="any-exists-policy-id"))
```
> or

```python
conn.auto_scaling.resume_policy("any-exists-policy-id")
```

### Pause Policy
```python
conn.auto_scaling.pause_policy(Policy(id="any-exists-policy-id"))
```

> or

```python
conn.auto_scaling.pause_policy("any-exists-policy-id")
```

## Group Instance

### List Group Instance
```python
query = {
    "lifecycle_state": "INSERVICE",   # INSERVICE, PENDING, REMOVEING
    "health_status": "INITIALIZING",  # INITIALIZING, NORMAL, ERROR
    "marker": 0,
    "limit": 20
}
instances = conn.auto_scaling.instances("group-id", **query)
for instance in instances:
    print instance
```


### Remove Instance
> remove and not delete instance

```python
instance_to_be_removed = "instance-id"
conn.auto_scaling.remove_instance(instance_to_be_removed)
```

> remove and delete instance

```python
instance_to_be_removed = "instance-id"
conn.auto_scaling.remove_instance(instance_to_be_removed,
                                  delete_instance=True)
```

### Batch Remove Instance
> batch remove but not delete instance

```python
group_of_instance = "group-id"
instances_to_be_removed = ["instance-id"]
conn.auto_scaling.batch_remove_instances(group_of_instance,
                                         instances_to_be_removed)
```

> remove and delete instance

```python
group_of_instance = "group-id"
instances_to_be_removed = ["instance-id"]
conn.auto_scaling.batch_remove_instances(group_of_instance,
                                         instances_to_be_removed,
                                         delete_instance=True)
```

### Batch Add Instance

```python
group_of_instance = "group-id"
instances_to_be_added = ["instance-id"]
conn.auto_scaling.batch_add_instances(group_of_instance,
                                      instances_to_be_added)
```


## Activity

### List Activity

```python
query = {
    "start_time": "2017-06-22T01:21:02Z",
    "end_time": "2017-06-22T15:00:02Z",
    "limit": 10
}
activities = conn.auto_scaling.activities(self.group, **query)
for activity in activities:
    print activity
```

## Quota

### List Quota

```
quotas = conn.auto_scaling.quotas()
for quota in quotas:
    print quota
```

### List Group Quota

```
auto_scaling_group = "group-id"
quotas = conn.auto_scaling.quotas(group=auto_scaling_group)
for quota in quotas:
    print quota
```