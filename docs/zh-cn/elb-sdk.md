# ELB SDk

HuaWei OpenStack `elastic load balancer` service SDK
- service entry: `connection.load_balancer`
- service type: `load_balancer`

## API document
Not provided for now.

## SDK document

### initial SDK client
You can find how to initial SDK client in the [quickstart](huawei-sdk?id=_2-build-v3-client) page .

### List load-balancer
```python
query = {
    vip_address='192.168.2.36'
}
# return a generator of load balancer instances
balancers = connection.load_balancer.load_balancers(**query)
for balancer in balancers:
    print balancer
```

### Create Zone
```java
// 待补充
```



