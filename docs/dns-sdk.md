# DNS SDK

HuaWei OpenStack `DNS` service SDK
- service entry: `conn.dns`
- service type: `dns`

## API document
Not provided for now.

## initial SDK client
You can find how to initial SDK client in the [quickstart](huawei-sdk?id=_2-build-v3-client) page .

## Zone
### List Zones
```python
query = {
    'zone_type': 'public', // filter by zone type, type includes `public` or `private`
    'limit': 10
}
zones = conn.dns.zones(**query)
for zone in zones:
    logging.info(zone)
```

### Create Zone

**1. create a private zone**
```python
_zone = {
    'name': 'gate.app.huawei.com',
    'description': 'This is an example zone.',
    'zone_type': 'private',
    'email': 'admin@huawei.com',
    'ttl': 500,
    'router': {
        'router_id': '5fbf2de5-c7e5-4ec5-92ef-1e0b128f729f',
        'router_region': 'eu-de'
    }
}
zone = conn.dns.create_zone(**_zone)
```

**2. create a public zone**
```python
_zone = {
    'name': 'app.huawei.com',
    'description': 'This is an example zone.',
    'zone_type': 'public',
    'email': 'admin@huawei.com',
    'ttl': 500
}
zone = conn.dns.create_zone(**_zone)
```

### Get Zone
```python
# Get Zone with zone_id
zone = conn.dns.get_zone(zone_id)

# or Zone instance with ID
zone = conn.dns.get_zone(Zone(id=zone_id))
```

### Delete Zone
```python
# Delete Zone with zone_id
conn.dns.delete_zone(zone_id, ignore_missing=True)

# or Zone instance with ID
conn.dns.delete_zone(Zone(id=zone_id), ignore_missing=False)
```

### Add Router(VPC) to Private Zone
```python
router = {
    'router_id': '62615060-5a38-42d4-a391-9b8a109da548',
    'router_region': 'eu-de'
}

# use zone-id
result = conn.dns.add_router_to_zone('zone-id', **router)
# use zone-instance
result = conn.dns.add_router_to_zone(Zone(id='zone-id'), **router)
```

### Remove Router(VPC) from Private Zone
```python
router = {
    'router_id': '62615060-5a38-42d4-a391-9b8a109da548',
    'router_region': 'eu-de'
}

# use zone-id
result = conn.dns.remove_router_from_zone('zone-id', **router)
# use zone-instance
result = conn.dns.remove_router_from_zone(Zone(id='zone-id'),
                                                **router)
```

## NameServer

### List Zone NameServers
```python
zone_id = 'ff8080825ca865e8015ca99563af004a'

# list zone nameservers with zone_id
nameservers = conn.dns.nameservers(zone_id)
# or with Zone instance with ID
nameservers = conn.dns.nameservers(Zone(id=zone_id))

for nameserver in nameservers:
    logging.info(nameserver)

```


## Recordset

### List Recordsets of Zone

```python
query = {
    'limit': 5
}
zone_id = 'ff8080825ca865e8015caa9f452700a8'
# use zone id as param
recordsets = conn.dns.recordsets(zone_id, **query)
# or use zone instance as param
# recordsets = conn.dns.recordsets(Zone(id=zone_id), **query)
for recordset in recordsets:
    logging.info(recordset)
```

### Create Recordset

```python
recordset = {
    "name": "api.turnbig.net",
    "description": "This is an example record set.",
    "type": "CNAME",
    "ttl": 3600,
    "records": [
        "www.turnbig.net"
    ]
}

zone_id = 'ff8080825ca865e8015caa9f452700a8'
conn.dns.create_recordset(zone_id, **recordset)
# or
conn.dns.create_recordset(Zone(id=zone_id), **recordset)
```

### Get Recordset
```python
zone = Zone(id='ff8080825ca865e8015caa9f452700a8')
recordset1 = conn.dns.get_recordset(zone, recordset_id)
recordset2 = conn.dns.get_recordset(zone, Recordset(id=recordset_id))
recordset3 = conn.dns.get_recordset(zone.id, recordset_id)
recordset4 = conn.dns.get_recordset(zone.id, Recordset(id=recordset_id))
```

### Delete Recordset
```python
zone = Zone(id='ff8080825ca865e8015caa9f452700a8')
recordset = Recordset(id='ff8080825ca865e8015caaaa0e1500ba')
conn.dns.delete_recordset(zone, recordset)
conn.dns.delete_recordset(zone.id, recordset.id)
```

### List all recordsets
```python
query = {
    'limit': 100
}
recordsets = conn.dns.all_recordsets(**query)
for recordset in recordsets:
    logging.info(recordset)
```

## PTR

### List PTR
```python
query = {
    'limit': 10
}
for ptr in conn.dns.ptrs(**query):
    logging.info(ptr)
```

### Setup PTR

```python
ptr = {
    'region': 'eu-de',                                          # required
    'floating_ip_id': '9e9c6d33-51a6-4f84-b504-c13301f1cc8c',   # required
    'ptrdname': 'www.turnbig.net',                              # required
    'description': 'HaveFun.lee - For Test',
    'ttl': 300,
}
ptr = conn.dns.create_ptr(**ptr)
```

### Get PTR
```python
region = 'eu-de'
floating_ip_id = '9e9c6d33-51a6-4f84-b504-c13301f1cc8c'
ptr = conn.dns.get_ptr(region, floating_ip_id)
```

### Restore PTR
```python
region = 'eu-de'
floating_ip_id = '9e9c6d33-51a6-4f84-b504-c13301f1cc8c'
conn.dns.restore_ptr(region, floating_ip_id)
```
