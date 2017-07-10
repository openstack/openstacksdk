# MRS SDK

HuaWei OpenStack `Map Reduce` Service SDK
- Service Entry: `conn.map_reduce`
- Service Type: `map-reduce`

## API documentation

Refer: [Official API documentation](https://docs.otc.t-systems.com/en-us/api/mrs/en-us_topic_0037324628.html)


## Data Source
### Create Data Source
```python
ds = {
    "name": "SDK-unittest",
    "url": "/sdk/unittest/input",
    "is_protected": False,
    "is_public": False,
    "type": "hdfs",
    "description": ""
}
data_source = conn.map_reduce.create_data_source(**ds)
```

### Update Data Source
```python
updated = {
    "name": "SDK-test",
    "type": "hdfs",
    "url": "/user/hadoop/input1",
    "description": "This is public input",
    "is_protected": True
}
data_source = conn.map_reduce.update_data_source("data_source_id", **updated)
```


### List Data Source
```python
query = dict(sort_by="-created_at", limit=20, marker="last-data-source-id")
data_sources = list(conn.map_reduce.data_sources(**query))
```

### Get Data Source Detail
```python
data_source = conn.map_reduce.get_data_source("data-source-id")
```

### Delete Data Source
```python
conn.map_reduce.delete_data_source("data-source-id")
```

### Cluster (TODO)
### Create Cluster And Execute a Job

!> TODO

### Add Nodes To Cluster
```
# node amount to be added to the cluster
expand_node_amount = 3
conn.map_reduce.expand_cluster("cluster-id", expand_node_amount)
```

### Remove Nodes of Cluster

?> Not supported for now

```
# node amount to be removed
reduce_node_amount = 3
# node instances to be removed
includes = ["instance-id-1", "instance-id-2"]
# node instances should not be removed
excludes = ["instance-id-3", "instance-id-4"]
conn.map_reduce.reduce_cluster("cluster-id",
                                reduce_node_amount,
                                includes=includes,
                                excludes=excludes)
```

### Get Cluster Detail

!> TODO

### Delete Cluster
```python
conn.map_reduce.delete_cluster("cluster-id")
```

> or

```python
conn.map_reduce.delete_cluster(Cluster(id="cluster-id"))

## Job Binary
### Create Job Binary
```python
binary = {
    "name": "SDK-unittests",
    "url": "/sdk/mapreduce/input1",
    "is_protected": False,
    "is_public": False,
    "description": ""
}
binary = conn.map_reduce.create_job_binary(**binary)
```

### Update Job Binary
```python
updated = {
    "url": "/sdk/unittest/input1",
    "description": "SDK unittests"
    "name": "new-name",
}
job_binary = conn.map_reduce.update_job_binary("binary-id", **updated)
```

### List Job Binary
```python
query = dict(sort_by="-created_at", limit=20, marker="last-job-binary-id")
job_binaries = list(conn.map_reduce.job_binaries(**query))
```

### Get Job Binary
```python
job_binary = conn.map_reduce.get_job_binary("job-binary-id")
```

### Delete Job Binary
```python
conn.map_reduce.delete_job_binary("job-binary-id")
```


## Job
### Create Job And Execute
```python
# TODO
```

### Create Job
```python
job = {
    "name": "SDK-unittests",
    "mains": [
        "job-binary-id-script"
    ],
    "libs": [
        "job-binary-id-input"
    ],
    "is_protected": False,
    "interface": [
    ],
    "is_public": False,
    "type": "MapReduce",
    "description": "SDK unittest, Feel Free to delete"
}
job = conn.map_reduce.create_job(**job)
```

### Update Job
```python
updated = {
    "name": "new-name",
    "type": "Spark",
    "description": "SDK Unittets"
}
_job = conn.map_reduce.update_job("job-id", **updated)
```

### Execute Job
```python
_job_execution = {
    "cluster_id": "cluster-id",
    "input_id": "job-binary-input-id",
    "output_id": "job-binary-output-id",
    "is_protected": False,
    "is_public": False,
    "job_configs": {
        "configs": {
            "mapred.map.tasks": "1",
            "mapred.reduce.tasks": "1"
        },
        "args": [
            "wordcount ",
            "arg2"
        ],
        "params": {
            "param2": "value2",
            "param1": "value1"
        }
    }
}

job_execution = conn.map_reduce.execute_job("job-id", **_job_execution)
```

### List Job
```python
query = dict(sort_by="-created_at", limit=20, marker="last-job-id")
jobs = list(conn.map_reduce.jobs(**query))
```

### Get Job Detail
```python
job = conn.map_reduce.get_job("job-id")
```

### List Job Executions
```python
query = {
    "id": "job-exe-id",
    "cluster_id": "cluster-id",
    "job_name": "job-name",
    "page_size": 20,
    "current_page": 2,
    "state": 3
}
executions = list(conn.map_reduce.job_exes(**query))
```

### Get Job Executions Detail
```python
conn.map_reduce.get_job_exe("job-exe-id")
# or
# conn.map_reduce.get_job_exe(JobExe(id="job-exe-id"))
```

### Delete Job
```python
conn.map_reduce.delete_job("job-id")
```


### Job Execution
### List Job Execution
```python
query = {
    "limit": 20,
    "sort_by": "-name",
    "marker": "job-execution-id"
}
executions = list(conn.map_reduce.job_executions(**query))
```

### Get Job Execution Detail
```python
job_execution = conn.map_reduce.get_job_execution("job-execution-id")
```

### Cancel Job Executions
```python
job_execution = conn.map_reduce.cancel_job_execution("job-execution-id")
```

### Delete Job Execution
```python
conn.map_reduce.delete_job_execution("job-execution-id")
```



