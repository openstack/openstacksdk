# VBS SDK

HuaWei OpenStack `Volume Backup` Service SDK
- Service Entry: `conn.volume_backup`
- Service Type: `volume-backup`

## API documentation
Refer: [Official API documentation](https://docs.otc.t-systems.com/en-us/api/vbs/en-us_topic_0061309333.html)

## Volume Backup

### Create Volume Backup
```python
# volume to be backuped
volume_id = "xxxxxx"
backup = {
    "volume_id": volume_id,
    "name": "volume-backup-xxxx",
    "description": "created by openstacksdk"
}
job = conn.volume_backup.create_backup(**backup)
```

### Restore Volume Backup
```python
volume_backup_id = "xxxxxxx"
# the volume restore to
volume_id = "xxxxxx"
job = conn.volume_backup.restore_backup(volume_backup_id, volume_id)
```

### Create Volume Backup(Native)
```python
volume_id = "c68ae7fb-0aa5-4a97-ab01-ed02c5b7e768"
snapshot_id = "2bb856e1-b3d8-4432-a858-09e4ce939389"
data = {
    "volume_id": volume_id,
    "snapshot_id": snapshot_id,
    "name": "native-volume-backup-1",
    "description": "created by openstacksdk"
}
backup = conn.volume_backup.create_native_backup(**data)
```

### List Volume Backup(Native)
```python
query = {
    "name": "some-backup",
    "status": "available",
    "volume_id": "0781095c-b8ab-4ce5-99f3-4c5f6ff75319",
    "marker": "some-backup-id",
    "limit": 10
}
backups = listconn.volume_backup.backups(**query))
```

### List Volume Backup Details(Native)
```python
query = {
    "name": "some-backup",
    "status": "available",
    "volume_id": "0781095c-b8ab-4ce5-99f3-4c5f6ff75319",
    "marker": "some-backup-id",
    "limit": 10
}
backups = listconn.volume_backup.backups(details=True, **query))
```

### Get Volume Backup Detail(Native)
```python
volume_backup_id = "xx"
volume_backup = conn.volume_backup.get_backup(volume_backup_id)
```

### Delete Volume Backup(Native)
```python
conn.volume_backup.delete_backup("volume_backup_id")
```

### Querying the Job Status
```python
# This API is not ready for now
# because the API version is not the same as other API
conn.volume_backup.get_job("job_id")
```


## Volume Backup Policy
### Create Volume Backup Policy
```python
data = {
    "remain_first_backup_of_curMonth": True,
    "rentention_num": 10,
    "frequency": 1,
    "start_time": "12:00",
    "status": "ON"
}
volume_backup_name = "SDK-backup-test-1"
policy = conn.volume_backup.create_backup_policy(volume_backup_name, **data)
```

### List Volume Backup Policy
```python
policies = list(conn.volume_backup.backup_policies())
```

### Update Volume Backup Policy
```python
updated = {
    "scheduled_policy": {
        "frequency": 5,
        "start_time": "01:00"
    }
}
policy = BackupPolicy(id="policy-id")
conn.volume_backup.update_backup_policy(policy, **updated)
```

### Delete Volume Backup Policy
```python
policy = BackupPolicy(id="policy-id")
conn.volume_backup.delete_backup_policy(policy)
```

### Link Resources to Volume Backup Policy
```python
policy = BackupPolicy(id="policy-id")
volumes = ["volume-id-1", "volume-id-2",]
conn.volume_backup.link_resources_to_policy(policy, volumes)
```

### Unlink Volume Backup Policy Resources
```python
policy = BackupPolicy(id="policy-id")
volumes = ["volume-id-1", "volume-id-2",]
conn.volume_backup.unlink_resources_of_policy(policy, volumes)
```

### Execute Volume Backup Policy
```python
policy = BackupPolicy(id="policy-id")
conn.volume_backup.execute_policy(policy)
```

### Enable Volume Backup Policy
```python
policy = BackupPolicy(id="policy-id")
conn.volume_backup.enable_policy(policy)
```


### Disable Volume Backup Policy
```python
policy = BackupPolicy(id="policy-id")
conn.volume_backup.disable_policy(policy)
```

### List Backup Policy Task
```python
query = {
    "id": "0781095c-b8ab-4ce5-99f3-4c5f6ff75319", # job_id works too
    "sort_dir": "asc",
    "sort_key": "created_at",
    "status": "RUNNING",
    "limit": 10,
    "offset": 10
}
backup_policy_id = "policy-id"
tasks = list(conn.volume_backup.tasks(backup_policy_id, **query))
```

