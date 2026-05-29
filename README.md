# 掌柜APP 接口自动化测试框架

华盟云平台掌柜APP的接口自动化测试框架，覆盖商户管理核心业务场景。

## 技术栈

| 技术 | 用途 |
|------|------|
| Python 3.x | 编程语言 |
| pytest | 测试框架 |
| requests | HTTP请求库 |
| PyYAML | 数据驱动 |
| pytest-html | 测试报告 |
| pytest-ordering | 用例执行顺序控制 |
| Faker | 测试数据生成 |
| python-dotenv | 环境变量管理 |

## 项目结构

```
zhanggui-app-test/
├── config/
│   └── config.py          # 环境配置（多环境支持、测试账号、门店配置）
├── api/
│   ├── client.py          # API客户端基类（统一请求、Token管理、重试机制）
│   ├── auth_api.py        # 认证模块API（登录/登出/Token刷新）
│   ├── store_api.py       # 门店模块API（CRUD、状态管理、统计）
│   ├── product_api.py     # 商品模块API（分类、商品、上下架）
│   ├── order_api.py       # 订单模块API（CRUD、状态流转、退款）
│   ├── payment_api.py     # 支付模块API（支付、退款、结算）
│   └── member_api.py      # 会员模块API（注册、余额、积分）
├── testcases/
│   ├── test_auth.py       # 认证模块测试（10个用例）
│   ├── test_store.py      # 门店模块测试（8个用例）
│   ├── test_product.py    # 商品模块测试（12个用例）
│   ├── test_order.py      # 订单模块测试（14个用例）
│   ├── test_payment.py    # 支付模块测试（14个用例）
│   └── test_member.py     # 会员模块测试（15个用例）
├── data/
│   └── test_data.yaml     # 数据驱动测试数据
├── fixtures/
│   └── common.py          # 通用测试fixtures
├── utils/
│   ├── logger.py          # 日志工具
│   ├── assertions.py      # 自定义断言
│   └── helpers.py         # 辅助工具（订单号生成、手机号生成等）
├── conftest.py            # pytest全局fixture
├── pytest.ini             # pytest配置
├── requirements.txt       # 依赖管理
├── .env.example           # 环境变量模板
└── README.md
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，填入测试环境的账号密码
```

### 3. 运行测试

```bash
# 运行全部测试
pytest

# 运行指定模块
pytest testcases/test_order.py -v

# 运行冒烟测试
pytest -m smoke -v

# 运行回归测试
pytest -m regression -v

# 运行指定模块标记
pytest -m order -v

# 生成HTML报告
pytest --html=reports/report.html --self-contained-html
```

### 4. 查看报告

运行后在 `reports/` 目录下生成HTML报告。

## 业务覆盖

### 认证模块（auth）
- 登录成功/失败场景
- Token管理（刷新、过期）
- 权限验证

### 门店模块（store）
- 门店列表（分页、搜索）
- 门店CRUD
- 门店状态切换（营业/歇业）
- 门店统计数据

### 商品模块（product）
- 商品分类管理
- 商品CRUD
- 商品上下架
- 批量操作

### 订单模块（order）
- 订单列表（分页、状态筛选、日期筛选）
- 订单状态流转（待确认→已确认→已完成、取消）
- 订单退款
- 边界测试（空商品、零数量）

### 支付模块（payment）
- 多支付方式（微信、支付宝、现金、会员余额）
- 支付异常（0元、负数、无效方式）
- 退款（全额、部分、超额）
- 日结算数据

### 会员模块（member）
- 会员注册（含重复校验）
- 会员余额查询和充值（多档位赠送）
- 会员积分查询
- 会员搜索

## 测试用例统计

| 模块 | 用例数 | 覆盖范围 |
|------|--------|----------|
| 认证 | 8 | 登录/登出/Token/权限 |
| 门店 | 26 | CRUD/状态/统计/员工/公告/权限/导出 |
| 商品 | 32 | 分类/商品/上下架/批量/库存/规格/标签/排序/图片/搜索 |
| 订单 | 23 | CRUD/状态流转/退款/备注/批量/统计/导出/日志/边界 |
| 支付 | 26 | 多支付方式/异常/退款/状态/统计/渠道/验证/关闭/结算/边界 |
| 会员 | 32 | 注册/余额/积分/搜索/等级/兑换/消费记录/标签/挂失/统计/边界 |
| 并发测试 | 15 | 并发登录/下单/支付/库存/充值/注册/状态变更/查询/退款 |
| 安全测试 | 26 | SQL注入/XSS/越权/敏感信息/认证绕过/参数篡改/暴力破解 |
| 性能测试 | 22 | 响应时间/分页性能/搜索性能/统计性能/批量性能/超时/大数据量 |
| 数据驱动 | 18 | 参数化：登录/支付/充值/状态/搜索/分类/分页/排序/退款 |
| 边界条件 | 32 | 空值/极值/特殊字符/长度边界/类型错误/负数/小数/重复请求 |
| **合计** | **260** | |

## 核心设计亮点

1. **分层架构**: API封装层 / 测试用例层 / 数据层 / 工具层，职责清晰
2. **API客户端基类**: 统一请求处理、Token管理、日志记录、自动重试
3. **多环境支持**: test/staging/prod环境一键切换
4. **环境变量管理**: 敏感配置通过 .env 文件管理，安全可控
5. **数据驱动**: YAML + pytest.mark.parametrize，覆盖多组业务数据
6. **Session级Fixture**: Token和API客户端复用，提升执行效率
7. **业务场景覆盖**: 不仅测试CRUD，还测试状态流转、异常处理、边界条件
8. **自定义断言**: 封装业务断言（分页结构、状态码、字段校验）
9. **智能跳过**: 数据不足时用 pytest.skip() 明确标记，避免静默失败

## 项目背景

本项目基于华盟云平台掌柜APP的实际业务场景设计，覆盖商户日常运营的核心功能模块。掌柜APP是面向线下商户的移动端管理工具，支持门店管理、商品管理、订单处理、支付收款、会员管理等功能。

## License

MIT
