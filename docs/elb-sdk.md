# ELB SDk

HuaWei OpenStack `Elastic Load Balancer` Service SDK
- Service Entry: `conn.load_balancer`
- Service Type: `load_balancer`

## API documentation

Refer: [Official API documentation](https://docs.otc.t-systems.com/en-us/api/elb/en-us_topic_0020100167.html)

## Load Balancer

### Create Load Balancer

```python
lb_name = "SDK-test-lb-1"
vpc_id = "xxxx"
load_balancer = {
    "name": name,
    "vpc_id": vpc_id,
    "bandwidth": 1,
    "type": "External",
    "is_admin_state_up": True
}
job = conn.load_balancer.create_load_balancer(**load_balancer)
job_detail = conn.load_balancer.get_job(job.job_id)
```

### Delete Load Balancer

```python
lb_id = "xxxxxxxxxx"
job = conn.load_balancer.delete_load_balancer(lb_id)
# job = conn.load_balancer.delete_load_balancer(LoadBalancer(id=lb_id))
job_detail = conn.load_balancer.get_job(job.job_id)
```

### Update Load Balancer

```python
updated = {
    "description": "lb created by functional test",
    "bandwidth": 2,
    "admin_state_up": True
}
load_balancer_id = "xxx"
job = conn.load_balancer.update_load_balancer(load_balancer_id, **updated)
job_detail = conn.load_balancer.get_job(job.job_id)
```

### Get Load Balancer Detail

```python
load_balancer_id = "xxx"
lb = conn.load_balancer.get_load_balancer(load_balancer_id)
```

### List Load Balancer

```python
# all filter condition is optional
query = {
    "id": "id",
    "name": "name",
    "status": "status",
    "type": "type",
    "description": "description",
    "vpc_id": "vpc_id",
    "vip_subnet_id": "vip_subnet_id",
    "vip_address": "vip_address",
    "security_group_id": "security_group_id",
    "is_admin_state_up": True
}
lbs = list(conn.load_balancer.load_balancers(**query))
```


## Listener

### Create Listener
```python
lb_id = load_balancer_id
listener_name = "Listener_Test"
listener_attrs = {
    "name": listener_name,
    "loadbalancer_id": load_balancer_id,
    "protocol": "HTTP",
    "port": 10086,
    "backend_protocol": "HTTP",
    "backend_port": 80,
    "lb_algorithm": "roundrobin",
    "is_session_sticky": True,
    "sticky_session_type": "insert",
    "cookie_timeout": 60
}
listener = conn.load_balancer.create_listener(**listener_attrs)
```


### Delete Listener
```python
listener_id = "xxxxx"
conn.load_balancer.delete_listener(listener_id)
# conn.load_balancer.delete_listener(Listener(id=listener_id))
```

### Update Listener
```python
 updated = {
    "description": "listener created by functional test",
    "port": 10000
}
listener_id = "xxxxx"
listener = conn.load_balancer.update_listener(listener_id, **updated)
```

### Get Listener
```python
listener_id = "xxxxx"
listener = conn.load_balancer.get_listener(listener_id)
# listener = conn.load_balancer.get_listener(Listener(id=listener_id))
```

### List Listener
```python
# all filter condition is optional
query = {
    "id": "id",
    "name": "name",
    "loadbalancer_id": "loadbalancer_id",
    "description": "description",
    "status": "status",
    "healthcheck_id": "healthcheck_id",
    "certificate_id": "certificate_id",
    "port": 80,
    "protocol": "protocol",
    "backend_port": 9000,
    "backend_protocol": "backend_protocol",
    "lb_algorithm": "lb_algorithm",
}
listeners = list(conn.load_balancer.listeners(**query))
```

## Health Check
### Create Health Check
```python
listener_id = "xxxxxxxx"
health_check = {
    "listener_id": listener_id,
    "healthcheck_protocol": "HTTP",
    "healthcheck_connect_port": 80,
    "healthcheck_interval": 5,
    "healthcheck_timeout": 10,
    "healthcheck_uri": "/health",
    "healthy_threshold": 3,
    "unhealthy_threshold": 3
}
health_check = conn.load_balancer.create_health_check(**health_check)
```

### Delete Health Check
```python
health_check = HealthCheck(id="xxxx")
conn.load_balancer.delete_health_check(health_check)
# conn.load_balancer.delete_health_check(health_check.id)
```

### Update Health Check
```python
health_check = HealthCheck(id="xxxx")
updated = {
    "healthcheck_connect_port": 88,
    "healthcheck_interval": 5,
    "healthcheck_protocol": "HTTP",
    "healthcheck_timeout": 10,
    "healthcheck_uri": "/",
    "healthy_threshold": 3,
    "unhealthy_threshold": 2
}

health_check = conn.load_balancer.update_health_check(health_check, **updated)
```

### List Health Check
```python
health_check = HealthCheck(id="xxxx")
health_check = conn.load_balancer.get_health_check(health_check)
# health_check = conn.load_balancer.get_health_check(health_check.id)
```


## Backend Member
### Add Backend Member
?> 1. Remember the ECS(Member) should be in the same VPC as load-balancer's VPC
?> 2. address is the VPC internal IP of the ECS

```python
listener_id = "listener-id"
servers = [{"server_id": "server-id-1", "address": "192.168.1.100"},
           {"server_id": "server-id-2", "address": "192.168.1.200"},]
# return a asynchronous Task
job = conn.load_balancer.add_members_to_listener(listener_id, servers)
# Querying Asynchronous Task Status
job_detail = conn.load_balancer.get_job(job.id)
```

### Remove Backend Member
```python
listener_id = "listener-id"
member_ids = ["server-id-1", "server-id-2",]
job = conn.load_balancer.remove_members_of_listener(listener_id, member_ids)
# Querying Asynchronous Task Status
job_detail = conn.load_balancer.get_job(job.id)
```

### List Backend Member
```python
listener_id = "listener-id"
servers = list(conn.load_balancer.listener_members(listener_id))
```

## Certificate
### Create Certificate
```python
cert = {
    "name": name,
    "certificate": "-----BEGIN CERTIFICATE-----\nMIIDXTCCAkWgAwIBAgIJANoPUy2NktS6MA0GCSqGSIb3DQEBBQUAMEUxCzAJBgNV\nBAYTAkFVMRMwEQYDVQQIDApTb21lLVN0YXRlMSEwHwYDVQQKDBhJbnRlcm5ldCBX\naWRnaXRzIFB0eSBMdGQwHhcNMTYwNjIyMDMyOTU5WhcNMTkwNjIyMDMyOTU5WjBF\nMQswCQYDVQQGEwJBVTETMBEGA1UECAwKU29tZS1TdGF0ZTEhMB8GA1UECgwYSW50\nZXJuZXQgV2lkZ2l0cyBQdHkgTHRkMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIB\nCgKCAQEArmUUhzm5sxxVr/ku4+6cKqnKgZvDl+e/6CNCAq8YMZXTpJP64DjDPny9\n+8s9MbFabEG3HqjHSKh3b/Ew3FXr8LFa9YuWuAi3W9ii29sZsOwmzIfQhIOIaP1Y\nNR50DDjbAGTaxzRhV40ZKSOCkaUTvl3do5d8ttD1VlF2r0w0DfclrVcsS5v3kw88\n9gJ3s3hNkatfQiSt4qLNMehZ8Xofx58DIAOk/f3Vusj3372PsJwKX39cHX/NpIHC\nHKE8qaGCpDqv0daH766eJ065dqO9DuorXPaPT/nxw4PAccb9fByLrTams0ThvSlZ\no6V3yvHR4KN7mmvbViEmWRy+9oiJEwIDAQABo1AwTjAdBgNVHQ4EFgQUlXhcABza\n2SdXPYpp8RkWvKblCNIwHwYDVR0jBBgwFoAUlXhcABza2SdXPYpp8RkWvKblCNIw\nDAYDVR0TBAUwAwEB/zANBgkqhkiG9w0BAQUFAAOCAQEAHmsFDOwbkD45PF4oYdX+\ncCoEGNjsLfi0spJ6b1CHQMEy2tPqYZJh8nGuUtB9Zd7+rbwm6NS38eGQVA5vbWZH\nMk+uq5un7YFwkM+fdjgCxbe/3PMkk/ZDYPHhpc1W8e/+aZVUBB2EpfzBC6tcP/DV\nSsjq+tG+JZIVADMxvEqVIF94JMpuY7o6U74SnUUrAi0h9GkWmeYh/Ucb3PLMe5sF\noZriRdAKc96KB0eUphfWZNtptOCqV6qtYqZZ/UCotp99xzrDkf8jGkm/iBljxb+v\n0NTg8JwfmykCj63YhTKpHf0+N/EK5yX1KUYtlkLaf8OPlsp/1lqAL6CdnydGEd/s\nAA==\n-----END CERTIFICATE-----",
    "private_key": "-----BEGIN RSA PRIVATE KEY-----\nMIIEpAIBAAKCAQEArmUUhzm5sxxVr/ku4+6cKqnKgZvDl+e/6CNCAq8YMZXTpJP6\n4DjDPny9+8s9MbFabEG3HqjHSKh3b/Ew3FXr8LFa9YuWuAi3W9ii29sZsOwmzIfQ\nhIOIaP1YNR50DDjbAGTaxzRhV40ZKSOCkaUTvl3do5d8ttD1VlF2r0w0DfclrVcs\nS5v3kw889gJ3s3hNkatfQiSt4qLNMehZ8Xofx58DIAOk/f3Vusj3372PsJwKX39c\nHX/NpIHCHKE8qaGCpDqv0daH766eJ065dqO9DuorXPaPT/nxw4PAccb9fByLrTam\ns0ThvSlZo6V3yvHR4KN7mmvbViEmWRy+9oiJEwIDAQABAoIBACV47rpHuxEza24O\nevbbFI9OQIcs8xA26dN1j/+HpAkzinB4o5V+XOWWZDQwbYu58hYE4NYjqf6AxHk3\nOCqAA9yKH2NXhSEyLkP7/rKDF7geZg/YtwNiR/NXTJbNXl4p8VTaVvAq3yey188x\nJCMrd1yWSsOWD2Qw7iaIBpqQIzdEovPE4CG6GmaIRSuqYuoCfbVTFa6YST7jmOTv\nEpG+x6yJZzJ4o0vvfKbKfvPmQizjL+3nAW9g+kgXJmA1xTujiky7bzm2sLK2Slrx\n5rY73mXMElseSlhkYzWwyRmC6M+rWALXqOhVDgIGbaBV4IOzuyH/CUt0wy3ZMIpv\nMOWMNoECgYEA1LHsepCmwjlDF3yf/OztCr/DYqM4HjAY6FTmH+xz1Zjd5R1XOq60\nYFRkhs/e2D6M/gSX6hMqS9sCkg25yRJk3CsPeoS9v5MoiZQA8XlQNovcpWUI2DCm\naZRIsdovFgIqMHYh/Y4CYouee7Nz7foICzO9svrYrbOIVmMwDVJ8vzMCgYEA0ebg\nm0lCuOunyxaSBqOv4Q4sk7Ix0702dIrW0tsUJyU+xuXYH1P/0m+t4/KUU2cNwsg3\njiNzQR9QKvF8yTB5TB4Ye/9dKlu+BEOskvCpuErxc6iVJ+TZOrQDDPNcq56qez5b\nvv9EDdgzpjkjO+hS1j3kYOuG11hrP4Pox4PijqECgYEAz6RTZORKqFoWsZss5VK3\np0LGkEkfw/jYmBgqAQhpnSD7n20hd1yPI2vAKAxPVXTbWDFLzWygYiWRQNy9fxrB\n9F7lYYqtY5VagdVHhnYUZOvtoFoeZFA6ZeAph9elGCtM3Lq3PD2i/mmncsQibTUn\nHSiKDWzuk8UtWIjEpHze5BkCgYEAifD9eG+bzqTnn1qU2pIl2nQTLXj0r97v84Tu\niqF4zAT5DYMtFeGBBI1qLJxVh7342CH2CI4ZhxmJ+L68sAcQH8rDcnGui1DBPlIv\nDl3kW3280bJfW1lUvPRh8NfZ9dsO1HF1n75nveVwg/OWyR7zmWIRPPRrqAeua45H\nox5z/CECgYBqwlEBjue8oOkVVu/lKi6fo6jr+0u25K9dp9azHYwE0KNHX0MwRALw\nWbPgcjge23sfhbeqVvHo0JYBdRsk/OBuW73/9Sb5E+6auDoubCjC0cAIvs23MPju\nsMvKak4mQkI19foRXBydB/DDkK26iei/l0xoygrw50v2HErsQ7JcHw==\n-----END RSA PRIVATE KEY-----"
}
cert = conn.load_balancer.create_certificate(**cert)
```

### Delete Certificate
```python
cert_id = "any-cert-id"
conn.load_balancer.delete_certificate(cert_id)
# conn.load_balancer.delete_certificate(Certificate(id=cert_id))
```

### Update Certificate
```python
cert_id = "any-cert-id"
updated = {
    "name": "cert-bky",
    "description": "certificate"
}
cert = conn.load_balancer.update_certificate(cert_id, **updated)
```

### List Certificate
```python
certificates = list(conn.load_balancer.certificates())
```

## Quota
### List Quota
```python
quotas = list(conn.load_balancer.quotas())
```


## Asynchronous Task

### Querying Asynchronous Task Status
```python
job_id = "xxxxx"
job = conn.load_balancer.get_job(job_id)
```
