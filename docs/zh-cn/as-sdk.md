# AutoScalingService SDK

HuaWei OpenStack `AutoScaling` service SDK
- service entry: `conn.auto_scaling`
- service type: `auto-scaling`

## API document
Not provided for now.

## initial SDK client
You can find how to initial SDK client in the [quickstart](huawei-sdk?id=_2-build-v3-client) page .

## Configs

### List Configs

> Query parameter ``dimensions`` could at most have three items

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
configs = conn.auto_scaling.get_config("any-exists-config-id")
```

> or

```python
configs = conn.auto_scaling.get_config(Config(id="any-exists-config-id"))
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
