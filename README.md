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

## 项目结构

```
zhanggui-app-test/
├── config/
│   └── config.py          # 环境配置（多环境支持、测试账号、门店配置）
├── api/
│   ├── client.py          # API客户端基类（统一请求、Token管理）
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
├── utils/
│   ├── logger.py          # 日志工具
│   ├── assertions.py      # 自定义断言
│   └── helpers.py         # 辅助工具（订单号生成、手机号生成等）
├── conftest.py            # pytest全局fixture
├── pytest.ini             # pytest配置
├── requirements.txt       # 依赖管理
└── README.md
```

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

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行测试

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

### 3. 查看报告

运行后在 `reports/` 目录下生成HTML报告。

## 测试用例统计

| 模块 | 用例数 | 覆盖范围 |
|------|--------|----------|
| 认证 | 10 | 登录/登出/Token/权限 |
| 门店 | 8 | CRUD/状态/统计 |
| 商品 | 12 | 分类/商品/上下架/批量 |
| 订单 | 14 | CRUD/状态流转/退款/边界 |
| 支付 | 14 | 多支付方式/异常/退款/结算 |
| 会员 | 15 | 注册/余额/积分/搜索 |
| **合计** | **73** | |

## 核心设计亮点

1. **分层架构**: API封装层 / 测试用例层 / 数据层 / 工具层，职责清晰
2. **API客户端基类**: 统一请求处理、Token管理、日志记录
3. **多环境支持**: test/staging/prod环境一键切换
4. **数据驱动**: YAML + pytest.mark.parametrize，覆盖多组业务数据
5. **Session级Fixture**: Token和API客户端复用，提升执行效率
6. **业务场景覆盖**: 不仅测试CRUD，还测试状态流转、异常处理、边界条件
7. **自定义断言**: 封装业务断言（分页结构、状态码、字段校验）

## 项目背景

本项目基于华盟云平台掌柜APP的实际业务场景设计，覆盖商户日常运营的核心功能模块。掌柜APP是面向线下商户的移动端管理工具，支持门店管理、商品管理、订单处理、支付收款、会员管理等功能。

## License

MIT
