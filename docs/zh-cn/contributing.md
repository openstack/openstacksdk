# 贡献代码

本节的主要内容节取自自官方的 [Contributing to the OpenStack SDK](https://developer.openstack.org/sdks/python/openstacksdk/contributors/index.html) 文档。为了避免翻译过程带来的理解偏差，我们强烈建议您直接阅读官方的文档。

本节文档的目标读者是那些想要在该SDK基础上进行开发或者代码修订的开发者。如果你只是想获取如何使用该SDK的文档，请查阅 [快速开始](zh-cn/quickstart.md)。


?> 这份文档只节取了跟SDK的设计相关的内容，官方的文档提供了更多详尽的内容。

## 项目结构

```
project
   |- doc            // 官方的文档目录，基于sphinx构建
   |- docs           // 本次新增的SDK的文档目录，基于docsify生成
   |- openstack      // SDK主目录
         |- compute         // compute SDK
         |- dns             // DNS SDK
         |- cloud_eye       // CES SDK
         |- ....
         |- resource2.py    // 资源对象的抽象封装
         |- session.py      // 认证相关
         |- proxy2.py       // Service SDK业务实现包装，封装了session和resource的API
         |- profile.py      // 服务申明
         |- connection.py   // 业务主入口
```

如上面的文件结构所示，项目的一级目录 `openstack`，它下面包含了实现SDK的所有代码。

- openstack目录下的各个模块，是SDK的基础，所有的SDK都是在这些模块的基础上构建的。
- openstack目录下的每个包，都对应了一个SDK的实现。比如`openstack.compute`对应的是`compute`服务

## 基础模块

基础模块是整个SDK开发的基石。`openstack` 目录下的直属模块都属于基础模块。SDK经历了一些版本的更迭，所以你会发现，`proxy` 和 `resource` 都有两个版本。新的SDK开发都基础 `proxy2` 和 `resource2`, 在所有的SDK迁移完成后，会删掉版本一，并将版本二的命名改回去。

在开发工程中，我们需要了解 `session`, `resource`, `proxy`, `connection` 这几个模块的作用。

### Session

?> openstack.session.Session

Session 对HTTP(request)请求做了一层抽象封装，并对外提供了简易的接口用于发送OpenStack的API请求。Session 主要封装了如下的功能：

- 从Openstack的认证过程中获取各类服务的Endpoint，并为各类服务的HTTP请求自动加上Endpoint
- 将OpenStack认证的token自动的注入到HTTP请求中，使用方只需要关注HTTP请求本身，而无需处理任何认证相关的逻辑。
- 加载各类服务的对应配置，并在请求时自动应用这些配置。比如，我们可以设置服务的版本，请求的时候，它会自动将请求切换到对应的版本上。

### Resource

?> openstack.resource.Resource

`Resource`是实现任意Service的基类。每个`Resource`的继承类都对应着OpenStack Service REST API所操作的资源。比如，`openstack.compute.v2.server.Server`对应着 `Compute`服务的 https://openstack/v2/servers 资源。

Resource基类通过封装资源对象的REST API，从而提供了各类资源的 CRUD 功能。他能够自动拼装各种不同操作所对应的URL，自动为不同的操作选择合适的HTTP方法，并使用`Session`来发送请求，从而完成整个REST API的功能。当然，上诉这些封装是建立 OpenStack REST API的统一规范的前提下。比如：

- 创建资源，POST请求，使用的URL是 /资源名s
- 查询列表，GET请求，使用的URL是 /资源名s
- 查询资源对象详情，GET请求，URL是 /资源名s/对象ID
- 分页使用 marker 和 limit ，marker为上一页最后一条记录的ID
- 还有很多其他的API规范...

由于所有的API都是这一套规则，所以，Resource的封装才成为可能。

REST API通过HTTP发送和接收的字段在Resource的继承类里都体现为一个属性。属性有三种类型，Body, Header, URI, 这三种类型都是 openstack.resource2._BaseComponent 的实现。这个属性的名称应该和服务端要求的属性名保持一致，而属性的命名可以和服务端不一样，可以按照python的风格，符合PEP8规则来进行命名。在发送HTTP请求时，Resource会自动将数据在二者之间进行映射。比如，下面的Server类表示，REST API中的属性名为`os-flavor-access:is_public`, 对应的python代码中为 `is_public`, 类型为bool。

```
class Server(Resource):
    is_public = resource.Body('os-flavor-access:is_public', type=bool)
```


每个Resource都支持不同的操作，为此Resource有8个属性类来定义他支持那些操作以及如何进行这些操作。在进行对应的操作前，Resource会验证这6个属性。
```
    #: 创建资源
    allow_create = False
    #: GET请求
    allow_get = False
    #: 更新资源
    allow_update = False
    #: 删除资源
    allow_delete = False
    #: 查询资源列表
    allow_list = False
    #: HEAD请求
    allow_head = False
    #: 使用PATCH方法来更新资源
    patch_update = False
    #: 使用PUT方法来创建资源
    put_create = False
```

Resource类中的 `base_path` 属性是用来定义资源的请求 URL，比如compute服务的Server资源的的URL为`/servers`。当然，还有些资源的URL里包含有动态属性，这时候，我们可以使用python的 `string replacement`来解决这个问题，比如 `/servers/%(server_id)s/ips`


Resource类中的 `resource_key` 和 `resources_key` 是用来接收服务端的返回值的时候使用的。有时候，服务端API的返回值将资源对象包装在一个子节点中，这些时候，我们就需要设置这两个属性来告诉Resource从哪里获取到返回值。比如, 如下的返回值，我们就需要将 resource_key 设置为 `server` 来获取server节点下的内容。
```json
{
      "server": {
            "id": "xxx"
      }
}
```

同理，resources_key 是在查询列表的返回值解析中使用的。

!> 新的SDK中，这两个key都支持多级节点，通过 `.` 来分隔节点。

### Proxy

?> openstack.proxy2.Proxy

每个Service都要继承`Proxy`实现一个自己的proxy模块，这个模块应该放在 `openstack/<service-type>/v<version>/_proxy.py`。比如，v2版本的 compute 服务的Proxy，对应的模块为 openstack/compute/v2/_proxy.py。

Proxy类将 `Session` 和 `Resource` 组装起来，并对外提供了更友好的接口。有了Proxy，用户就不再需要自己管理 Session 和使用 `Resource` 中的各类HTTP抽象接口（get, post, put），而是直接使用 `list`, `get`, `update` 这种更直观的接口。

可以这么理解，Proxy类对Resource做了一层封装代理，把一些更高层的通用代码进行了封装。使得访问REST API更加的容易。他所有的实现，都是在Resource的基础上进行的，Resource是Proxy的底层实现。比如：


### Connection

?> openstack.connection.Connection

`Connection` 主要做了两件事情：

- 封装Session，实现OpenStack认证相关的工作
- 初始化各个Service的`Proxy`, 并将Service挂载到Connection实例中

这样用户可以通过 Connection->Proxy->Resource 这个链条对所有的Resource进行操作。比如：

```python
   conn     proxy  resource
    |         |       |
connection. volume.volumes()
connection.compute.servers()
connection.network.networks()

```


## 添加功能

这节以一个例子来展示如何新增功能

### 命名约定

- 模块名称都是小写，多个单词以下划线分隔。比如，`openstack.object_store`
- 类名义大写字母开头，多个单词每个单词的首字母都是大写。比如，`ServerMetadata`
- 类属性，类方法，都是小写并以下划线分隔，比如，`allow_list`，`get_data`

### Services

OpenStack SDK中的服务通常以程序名来命名而不是项目名。比如，我们熟知的“Nova”项目，在OpenStack SDK中，我们称之为“compute” 。

下面的例子，我们以创建一个名称为"Fake"的服务为例，我们会在openstack下，创建一个faka的包。所有的Fake服务相关的代码，都会放在 `openstack.fake` 包下。

现在，我们开始创建 Service，它的代码非常简单，

> openstack/fake/fake_service.py

```
from openstack import service_filter


class FakeService(service_filter.ServiceFilter):
    """The fake service."""

    valid_versions = [service_filter.ValidVersion('v2')]

    def __init__(self, version=None):
        """Create a fake service."""
        super(FakeService, self).__init__(service_type='fake', version=version)
```

下一步，我们要开始创建Resource。

### Resource

Resource的命名是根据服务端对资源的命名来的，常见的命名方式是使用REST API中的URI。现在我们假定要对一个名为 Fake 的资源进行操作。

> openstack/fake/v2/fake.py

```
# Apache 2 header omitted for brevity

from openstack.fake import fake_service
from openstack import resource2


class Fake(resource2.Resource):
    resource_key = "resource"
    resources_key = "resources"
    base_path = "/fake"
    service = fake_service.FakeService()

    allow_create = True
    allow_update = True
    allow_delete = True
    allow_list = True
    allow_head = True

    #: The transaction date and time.
    timestamp = resourc2.Body("x-timestamp")
    #: The name of this resource.
    name = resource2.Body("name")
    #: The value of the resource. present in the header.
    value = resource2.Header("x-resource-value")
    #: Is this resource cool? If so, set it to True.
    #: This is a multi-line comment about cool stuff.
    cool = resource2.Body("cool", type=bool)
```

看上面的代码示例，所有的资源对象都是继承 openstack.resource2.Resource，然后根据该资源的实际情况来覆盖一些基础属性，就可以完成对应的CRUD操作。

**1. resource_key 和 resources_key**

这两个属性是根据服务端返回的数据结构来定的，默认值都是 None，当返回的JSON对象就是你想要的数据的时候，就不需要设置这两个key。比如：
```json
{
    "name": "Ernie Banks",
    ....
}
```

但是，在本例中，Fake 资源返回的数据把 Fake对象放在了 "resources" key 节点下，比如：

```
{
    "resources": [
        {
            "name": "xxx",
            ....
        }
    ]
}
```

这时候，我们就需要设置 `resources_key` 为 `resources`, 同理，在获取详情的时候，返回的对象是放在 `resource` key 下面的。

**2. base_path**

base_path 用来设置资源的请求路径。在本例中，值为 `/fake`，那么对应的，会自动使用下表的URI：

|  操作  |      URI      |
|:------:|:-------------:|
|  list  |     /fake     |
|   get  | /fake/fake-id |
| create |     /fake     |
| update | /fake/fake-id |
| delete | /fake/fake-id |


**3. service**

service 属性用于定义该资源属于哪个service，参见[上一节](zh-cn/contributing?id=services)


**4.Supported Operations**

用于指定资源支持哪些操作，在 [Resource](zh-cn/contributing?id=resource) 中已经说明过了

```
    allow_create = True
    allow_update = True
    allow_delete = True
    allow_list = True
    allow_head = True
```

**5. 文档**

Openstack SDk 使用Sphinx的autodoc功能来为每个Resource生成API文档。这些覆盖的属性不需要添加注释，其他新增的属性需要添加注释，注释的格式是以 `#:` 开头。 

```
    #: Is this resource cool? If so, set it to True.
    #: This is a multi-line comment about cool stuff.
    cool = resource2.Body("cool", type=bool)
```