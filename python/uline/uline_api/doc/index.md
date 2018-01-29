## 概述

Uline为开发者提供了 REST API 接口，用来执行商户进件，查询结算金额等功能。

## API 域名

```
v1.uline.com
```


## 文案约定

在您阅读文档之前，请先熟悉我们的一些约定的说法，以便您的理解

**替代字符**
所有用尖括号 `<>` 包围的字符，均为需要根据实际情况做替换的地方，特别的，`<>` 仅作为文档中将其区分于其他字符，您在实际使用的时候，不需要加上 `<>`。


**变量名/假设值**
所有使用行内代码，例如 `dt_id`，则意味着这是一个变量名，相对应的，如果是行内代码加斜体的格式，例如 *`/url.path`*，则意味着这是我们为了方便举例假设的一个具体值。



## 请求方法

```sh
curl -X GET \
    http://v0.api.upyun.com/<bucket>/<path> \
    -H "Authorization: <your_authorization>" \
    -H "Date: <Wed, 29 Oct 2014 02:26:58 GMT>" \
    -H "Content-Length: <content_length>"
    # 其他可选参数...

```

> **注：**
>
> * `Authorization`, `Date` 这两个参数是必须的
> * `Authorization` 用于认证授权
> * `Content-Length` 在 `PUT`、`POST` 请求中必须设置
> * `Date` 为[格林尼治标准时间](http://zh.wikipedia.org/wiki/%E6%A0%BC%E6%9E%97%E5%B0%BC%E6%B2%BB%E5%B9%B3%E6%97%B6)（GMT 格式）


## 认证授权

Uline支持 HTTP 基本认证与签名认证两种认证授权方式。请根据需要任选其一。

### HTTP 基本认证
将ID和APIKEY拼接后以 Base64 编码后自行在请求头部加上 `Authorization` 字段：

```sh
curl -X GET \
    http://v0.api.upyun.com/<bucket>\
    -H "Authorization: Basic aWQ6cHNzd29yZA=="
```

### 签名认证
为了避免 HTTP 基本认证 Base64 可逆带来的安全隐患，REST API 还支持更为安全的签名认证

__签名格式__
```
Authorization: Uline <id>:<signature>
```

__签名（signature）算法__

签名所需的相关信息如下表：

|    所需信息    |                                           说明                                           |
|----------------|------------------------------------------------------------------------------------------|
| METHOD         | 请求方式，如：GET、POST、PUT、HEAD 等                                                    |
| PATH           | 请求路径，需 URL 编码处理 ([RFC 1738](http://tools.ietf.org/html/rfc1738 )) |
| DATE           | 请求日期，GMT 格式字符串 ([RFC 1123](http://tools.ietf.org/html/rfc1123))                |
| CONTENT_LENGTH | 请求内容长度，除 GET 等无实体请求外，需和请求头部的 `Content-Length` 一致                |
| APIKEY         | 渠道商/商户ID对应的API密匙                                                                         |

将上表所注的所有信息以 `&` 字符进行拼接（按表格从上至下的顺序）即（`METHOD&PATH&DATE&CONTENT-LENGTH&APIKEY`），并将所得字符串进行 MD5 散列，即得我们所需的 签名（signature）

> **注：**
>
> - 签名的有效期为 1 分钟。如果超过 1 分钟，则需重新生成签名。
> - GET，DELETE 操作的 CONTENT_LENGTH 为 0。

如：

请求方式为 *`GET`*，请求路径为 *`/v1/mchinlet/authtest`* ，请求时间 为 *`Fri, 02 Dec 2016 15:09:05 GMT`*，因为是 GET，所以 `CONTENT-LENGTH` 为 *`0`*，假设该用户ID为 *`1234567830`*，对应APIKEY为 *`0F222642F0FB5F5F3FCDE292516C1EF4`*那么：

签名（signature）即是对字符串 *`GET&/v1/mchinlet/authtest&Fri, 02 Dec 2016 15:09:05 GMT&0&0F222642F0FB5F5F3FCDE292516C1EF4`* 计算 md5 所得，即：*`87e8e9f3d3a1a1e73787bd3d39d21f7f`*，因此，只需在请求头部加上如下字段即可：

```
Authorization: Uline 1234567830:87e8e9f3d3a1a1e73787bd3d39d21f7f
```

