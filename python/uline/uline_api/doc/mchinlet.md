### 商户进件

```
POST /v1/mchinlet
```
***注意*** 该请求Content-Type为application/x-www-form-urlencoded，并不是application/json


#### 请求参数

|      参数      | 必选 |说明 |
|----------------|------|-----|
| mch_name          | 是 | 商户名称           |
| mch_short_name    | 是 | 商户简称              |
| city              | 是 | 城市                    |
| province          | 是 | 省份(如:广东省)     |
| address           | 是 | 联系地址              |
| mobile            | 是 | 手机号               |
| email             | 是 | 邮箱                |
| service_phone     | 是 | 服务电话              |
| bank_name         | 是 | 结算银行名称(如:中国人民银行鹿泉市支行)
| industry_name     | 是 | 行业类别(如:企业-生活/家居-鲜花/盆栽/室内装饰品) |
| balance_type      | 是 | 结算类型(对公:1 对私:2) |
| balance_name      | 是 | 结算户名              |
| balance_account   | 是 | 结算银行卡号码           |
| img_card_front    | 是 | 身份证正反面照片             |
| img_card_back     | 是 | 营业执照           |
| id_card_no        | 是 | 身份证号码             |
| contact           | 是 | 联系人               |
| wx_use_parent     | 否 | 商户是否使用appid标识(1表示不使用(不填选时为1), 2表示使用)   |
| payment_type1     | 是 | 微信扫码支付费率(万分率，如60)     |
| payment_type2     | 是 | 微信线下小额支付费率(万分率，如60)   |
| payment_type3     | 是 | 微信公众账号支付费率(万分率，如60)   |


#### 响应信息

初始化断点续传成功返回 `204` 状态码, 包括以下响应参数:

|      参数             |   说明  |
|----------------------|---------------------|
| ul_mchid          | uline商户号    |
| mch_pay_key       | 商户微信支付密匙  |
| wx_sub_mch_id     | 微信子商户号    |


#### 返回示例

```
{
  "content": {
    "ul_mchid": 100000012760
  },
  "code": 200
}
```

### 商户修改

```
POST /v1/mchinlet/update?mch_id=<商户的mch_id>
```
***注意*** 该请求Content-Type为application/x-www-form-urlencoded，并不是application/json


#### 请求参数

|      参数      | 必选 |说明 |
|----------------|------|-----|
| mch_name          | 是 | 商户名称           |
| mch_short_name    | 是 | 商户简称              |
| city              | 是 | 城市                    |
| province          | 是 | 省份(如:广东省)     |
| address           | 是 | 联系地址              |
| mobile            | 是 | 手机号               |
| email             | 是 | 邮箱                |
| service_phone     | 是 | 服务电话              |
| bank_name         | 是 | 结算银行名称(如:中国人民银行鹿泉市支行)
| industry_name     | 是 | 行业类别(如:企业-生活/家居-鲜花/盆栽/室内装饰品) |
| balance_type      | 是 | 结算类型(对公:1 对私:2) |
| balance_name      | 是 | 结算户名              |
| balance_account   | 是 | 结算银行卡号码           |
| img_card_front    | 是 | 身份证正反面照片             |
| img_card_back     | 是 | 营业执照           |
| id_card_no        | 是 | 身份证号码             |
| contact           | 是 | 联系人               |
| payment_type1     | 是 | 微信扫码支付费率(万分率，如60)     |
| payment_type2     | 是 | 微信线下小额支付费率(万分率，如60)   |
| payment_type3     | 是 | 微信公众账号支付费率(万分率，如60)   |


#### 响应信息

初始化断点续传成功返回 `204` 状态码, 包括以下响应参数:

|      参数             |   说明  |
|----------------------|---------------------|
| ul_mchid          | uline商户号    |


#### 返回示例

```
{
  "content": {
    "ul_mchid": 100000012760
  },
  "code": 200
}
```
