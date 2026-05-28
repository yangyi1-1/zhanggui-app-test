# 掌柜APP测试框架 — 项目详解与面试指南

## 一、框架架构图

```
┌─────────────────────────────────────────────────────────┐
│                    conftest.py                          │
│         (Fixture管理：登录、Token、API客户端)             │
└──────────────────────┬──────────────────────────────────┘
                       │ 提供已认证的API客户端
                       ▼
┌─────────────────────────────────────────────────────────┐
│              testcases/ (测试用例层)                     │
│  test_auth.py | test_store.py | test_product.py | ...   │
│         调用API方法 → 发送请求 → 断言验证                 │
└──────────────────────┬──────────────────────────────────┘
                       │ 调用
                       ▼
┌─────────────────────────────────────────────────────────┐
│                api/ (API封装层)                          │
│  client.py (基类) → auth_api / store_api / order_api ... │
│         封装接口路径、参数、统一请求处理                   │
└──────────────────────┬──────────────────────────────────┘
                       │ 继承
                       ▼
┌─────────────────────────────────────────────────────────┐
│              config/ (配置层)                            │
│         base_url、超时、测试账号、环境切换                 │
└─────────────────────────────────────────────────────────┘

辅助层：
├── utils/logger.py      — 日志记录（控制台+文件双输出）
├── utils/assertions.py  — 自定义断言（状态码、分页、字段校验）
├── utils/helpers.py     — 辅助工具（生成订单号、手机号等）
└── data/test_data.yaml  — 测试数据（数据驱动）
```

---

## 二、各层详解

### 2.1 配置层 — config/config.py

```python
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("BASE_URL", "https://test-api.zhanggui.huameng.com")
TIMEOUT = int(os.getenv("TIMEOUT", "15"))
TEST_ACCOUNTS = {
    "admin": {
        "phone": os.getenv("TEST_ADMIN_PHONE", "13800000001"),
        "password": os.getenv("TEST_ADMIN_PASSWORD", "test123456"),
    },
}
```

**为什么要单独抽配置？**
- 换环境（test/staging/prod）只改配置，不动代码
- 测试账号、超时时间等集中管理，方便维护
- 敏感信息通过环境变量管理，安全可控

**面试话术**：
> "我把所有可变的配置集中到config.py，支持多环境一键切换。敏感信息如账号密码通过环境变量管理，配合.env文件使用，既安全又方便。改环境只需要改一个变量，不用到处找代码。"

---

### 2.2 API封装层 — api/client.py（基类）

```python
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class APIClient:
    def __init__(self):
        self.session = requests.Session()  # 复用连接

        # 配置重试策略
        retry = Retry(total=3, backoff_factor=0.5, status_forcelist=[500, 502, 503, 504])
        self.session.mount("http://", HTTPAdapter(max_retries=retry))
        self.session.mount("https://", HTTPAdapter(max_retries=retry))

    def set_token(self, token):
        self.session.headers["Authorization"] = f"Bearer {token}"

    def _request(self, method, path, **kwargs):
        url = f"{self.base_url}{path}"
        response = self.session.request(method, url, **kwargs)
        logger.info(f"[{method}] {url}")  # 记录日志

        # 检查 Token 过期
        if response.status_code == 401:
            logger.warning("Token 已过期，请重新登录获取新 Token")

        return response
```

**为什么要有基类？**
- 统一处理请求（Token、日志、超时）
- 子类只关心接口路径和参数，不重复写请求逻辑
- 维护方便：改日志格式只改一处
- 内置重试机制，网络抖动不会导致误报

**面试话术**：
> "我设计了一个API客户端基类，封装了Token管理、请求发送、日志记录和自动重试。重试策略是3次，指数退避，针对5xx错误。所有业务API继承它，只写自己接口的路径和参数。这样代码复用率高，维护也方便，网络抖动不会导致测试误报。"

---

### 2.3 业务API层 — api/order_api.py（示例）

```python
class OrderAPI(APIClient):  # 继承基类
    def get_order_list(self, params=None):
        return self.get("/api/v1/orders", params=params)

    def create_order(self, data):
        return self.post("/api/v1/orders", json=data)

    def cancel_order(self, order_id, reason):
        return self.post(f"/api/v1/orders/{order_id}/cancel", json={"reason": reason})
```

**为什么要把API单独封装？**
- 测试用例里不用记URL，直接调方法
- 接口路径变了只改API层，不影响用例
- 方法名就是接口的语义，代码可读性强

**面试话术**：
> "我把每个业务模块的接口封装成独立的API类，方法名对应接口功能。比如order_api.get_order_list()，测试用例里直接调用，不用关心URL是什么。接口路径变了只改API层，用例不用动。"

---

### 2.4 测试用例层 — testcases/test_order.py（示例）

```python
@pytest.mark.order  # 打标记
class TestOrder:

    # 基本用例
    def test_get_order_list(self, order_api):
        response = order_api.get_order_list()
        assert_status_code(response, 200)

    # 参数化用例
    @pytest.mark.parametrize("amount", [100, 200, 500])
    def test_recharge(self, member_api, amount):
        response = member_api.recharge("MEM_001", amount)
        assert response.status_code == 200

    # 异常场景
    def test_create_order_empty_items(self, order_api):
        response = order_api.create_order({"items": []})
        assert response.json()["code"] != 0  # 应该失败
```

**三种用例类型**：
1. **正常流程**：验证功能能用
2. **参数化**：同一逻辑覆盖多组数据
3. **异常/边界**：验证系统对错误输入的处理

**面试话术**：
> "我的用例分三类：正常流程验证功能可用，参数化用例覆盖多组数据提高效率，异常和边界用例验证系统的健壮性。比如订单模块，我不仅测了创建、确认、完成的正常流程，还测了空商品、零数量这些边界情况。"

---

### 2.5 Fixture — conftest.py

```python
@pytest.fixture(scope="session")
def admin_token(auth_api):
    """登录一次，整个测试会话复用Token"""
    response = auth_api.login("13800000001", "test123456")
    token = response.json()["data"]["token"]
    return token

@pytest.fixture(scope="session")
def order_api(admin_token):
    """基于Token创建已认证的API客户端"""
    api = OrderAPI()
    api.set_token(admin_token)
    return api
```

**scope="session"是什么意思？**
- 整个测试过程只执行一次登录
- 所有用例共享同一个Token
- 比每个用例单独登录快很多

**面试话术**：
> "我用session级Fixture管理登录和Token，整个测试过程只登录一次，所有用例共享Token。这样既模拟了真实用户行为（登录一次持续操作），又提升了执行效率。"

---

### 2.6 工具层 — utils/

**assertions.py — 自定义断言**：
```python
def assert_status_code(response, expected_code):
    actual = response.status_code
    assert actual == expected_code, f"状态码不匹配: 期望{expected_code}, 实际{actual}"

def assert_pagination(data):
    assert "total" in data
    assert "list" in data
```

**为什么要封装断言？**
- 用例里一行代码搞定，不用重复写assert
- 失败信息更详细（包含URL和响应内容）
- 分页断言封装后，所有列表接口都能复用

**helpers.py — 辅助工具**：
```python
def generate_order_no():
    """生成唯一订单号"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_str = "".join(random.choices(string.digits, k=6))
    return f"ORD{timestamp}{random_str}"
```

**面试话术**：
> "我封装了自定义断言，比如assert_pagination()专门校验分页结构，assert_status_code()失败时会打印URL和响应内容，方便排查问题。还封装了订单号、手机号生成工具，避免测试数据重复。"

---

### 2.7 数据驱动 — data/test_data.yaml

```yaml
member:
  recharge:
    - amount: 100.00
      expected_bonus: 10.00
    - amount: 200.00
      expected_bonus: 30.00
    - amount: 500.00
      expected_bonus: 100.00
```

配合pytest.mark.parametrize使用：
```python
@pytest.mark.parametrize("amount,expected_bonus", [
    (100.00, 10.00),
    (200.00, 30.00),
    (500.00, 100.00),
])
def test_recharge(self, amount, expected_bonus):
    ...
```

**为什么用数据驱动？**
- 测试数据和代码分离，改数据不用改代码
- 同一用例覆盖多组数据，减少重复代码
- YAML格式易读，非开发人员也能看懂

---

## 三、面试项目介绍（2-3分钟版本）

### 开场（30秒）

> "我在华盟负责掌柜APP的测试工作，掌柜APP是面向线下商户的移动端管理工具，支持门店管理、商品管理、订单处理、支付收款、会员管理等功能。为了提升回归测试效率，我搭建了一套接口自动化测试框架。"

### 框架设计（1分钟）

> "框架采用分层架构，分为四层：
> - **配置层**：管理环境地址、测试账号、超时配置，支持多环境一键切换
> - **API封装层**：有一个基类统一处理Token、请求、日志，每个业务模块继承基类，封装自己的接口方法
> - **测试用例层**：用pytest组织用例，支持标记分类、参数化测试、fixture管理
> - **工具层**：自定义断言、日志记录、数据生成工具
>
> 数据驱动用YAML文件管理测试数据，用例和数据分离。"

### 覆盖范围（30秒）

> "目前覆盖了认证、门店、商品、订单、支付、会员6个核心模块，共73个用例。不仅测了CRUD，还测了订单状态流转、支付异常、退款边界等业务场景。"

### 成果（30秒）

> "上线后回归测试时间从3天缩短到4小时，发现了不少隐藏的接口问题。"

---

## 四、面试官可能问的问题及回答

### Q1: 为什么选择分层架构？

**回答**：
> "分层的好处是职责清晰、维护方便。比如接口路径变了，我只改API层，用例不用动。如果所有代码混在一起，改一个接口要到处找、到处改，容易遗漏。另外分层后代码复用率高，比如基类的请求方法所有模块都能用。"

---

### Q2: Token是怎么管理的？

**回答**：
> "我用pytest的session级Fixture管理Token。整个测试过程只登录一次，拿到Token后设置到请求头里，所有用例共享。这样既模拟了真实用户行为（登录一次持续操作），又提升了效率。如果Token过期，可以在Fixture里加刷新逻辑。"

---

### Q3: 怎么处理测试数据的？

**回答**：
> "我用两种方式：
> 1. **固定数据**：写在YAML文件里，用pytest.mark.parametrize做参数化，比如充值测试覆盖100、200、500三个档位
> 2. **动态数据**：用helpers工具类生成，比如订单号用时间戳+随机数，手机号用随机生成，避免数据重复冲突
>
> 测试前创建数据，测试后清理数据，保证用例独立性。"

---

### Q4: 用例是怎么组织和筛选的？

**回答**：
> "我用pytest的marker给用例打标记，比如@pytest.mark.smoke是冒烟测试，@pytest.mark.order是订单模块。运行时可以按标记筛选：
> - pytest -m smoke：只跑冒烟用例
> - pytest -m order：只跑订单模块
> - pytest testcases/test_order.py：只跑某个文件
>
> 这样CI/CD里可以配置不同场景跑不同用例。"

---

### Q5: 接口依赖怎么处理？（比如创建订单依赖商品）

**回答**：
> "我用Fixture的依赖链处理。比如order_api依赖admin_token，admin_token依赖auth_api的登录。Fixture的执行顺序是自动管理的，依赖的Fixture会先执行。
>
> 对于业务依赖，比如创建订单需要商品ID，我会在用例里先调用商品接口获取数据，再用返回值创建订单。"

---

### Q6: 怎么保证用例的稳定性？

**回答**：
> "几个关键点：
> 1. **用例独立**：每个用例自己准备数据、自己清理，不依赖其他用例的执行结果
> 2. **等待机制**：异步操作加等待和重试
> 3. **断言精确**：不仅断言状态码，还断言响应体结构和关键字段值
> 4. **日志追踪**：每个请求和响应都记日志，失败时能快速定位问题"

---

### Q7: 这个框架有什么可以改进的地方？

**回答**：
> "有几个方向可以优化：
> 1. **加Mock能力**：对第三方支付接口做Mock，不依赖真实环境
> 2. **加Allure报告**：比pytest-html更美观，支持截图、附件、步骤记录
> 3. **加CI/CD集成**：配置GitHub Actions或Jenkins，代码提交自动跑测试
> 4. **加性能测试**：用locust对核心接口做并发压测
> 5. **加数据清理**：测试后自动清理创建的测试数据，保证环境干净"

---

### Q8: 你在这个项目中遇到的最大挑战是什么？

**回答**：
> "最大的挑战是接口依赖的处理。比如订单流程涉及创建商品→创建订单→支付→退款，每一步都依赖上一步的返回值。我的解决方案是用Fixture链管理公共依赖，业务依赖在用例内部用setUp方式处理。另一个挑战是支付回调的测试，因为回调是异步的，我加了轮询等待机制来验证支付状态。"

---

### Q9: pytest的Fixture scope有哪些？你用了哪些？

**回答**：
> "scope有四种：
> - **function**：每个用例执行一次（默认）
> - **class**：每个测试类执行一次
> - **module**：每个模块执行一次
> - **session**：整个测试会话执行一次
>
> 我主要用了session级（登录Token、API客户端复用）和function级（测试数据准备）。session级提升效率，function级保证用例独立性。"

---

### Q10: 为什么要在 API 客户端加自动重试？

**回答**：
> "接口测试跑在测试环境，网络不稳定是常有的事。如果不加重试，网络抖动会导致测试误报，排查起来很浪费时间。我用 urllib3 的 Retry 配置了3次重试，指数退避（0.5s、1s、2s），只对 5xx 服务端错误重试，4xx 客户端错误不重试。这样既避免了误报，又不会掩盖真正的接口问题。"

---

### Q11: 敏感配置怎么管理的？

**回答**：
> "测试账号、密码这些敏感信息不能硬编码在代码里，我用环境变量管理。本地开发用 .env 文件，CI/CD 里用系统环境变量。config.py 里用 os.getenv() 读取，有默认值兜底。.env 文件加到 .gitignore，不提交到代码库。这样既安全又方便，不同环境可以用不同的配置。"

---

### Q12: 参数化测试有什么好处？举个例子？

**回答**：
> "参数化的好处是用同一段代码覆盖多组数据，减少重复代码。比如会员充值测试，我用参数化覆盖100元送10元、200元送30元、500元送100元三个档位：
>
> ```python
> @pytest.mark.parametrize("amount,expected_bonus", [
>     (100, 10), (200, 30), (500, 100),
> ])
> def test_recharge(self, amount, expected_bonus):
>     ...
> ```
>
> 如果不用参数化，这三个场景要写三个几乎一样的用例。参数化后一行数据就是一个场景，加新档位只加一行数据。"

---

## 五、简历写法建议

### 项目经历部分

```
项目名称：掌柜APP接口自动化测试框架
技术栈：Python + pytest + requests + PyYAML
项目描述：
    基于华盟云平台掌柜APP业务场景，搭建分层架构的API自动化测试框架，
    覆盖认证、门店、商品、订单、支付、会员6大核心模块，共73个测试用例。

主要工作：
    1. 设计分层架构（配置层/API封装层/用例层/工具层），职责清晰，易维护
    2. 封装API客户端基类，统一Token管理、请求处理、日志记录
    3. 使用pytest.mark.parametrize实现数据驱动，覆盖多组业务数据
    4. 用session级Fixture管理登录和Token，提升执行效率
    5. 封装自定义断言和辅助工具，提升用例编写效率
    6. 覆盖正常流程、异常场景、边界条件，保障接口质量

项目成果：
    回归测试时间从3天缩短至4小时，效率提升85%
```

---

## 六、学习路径建议

| 优先级 | 学习内容 | 目标 |
|--------|----------|------|
| 1 | 理解本框架每一层的作用 | 面试能讲清楚 |
| 2 | 自己手动跑一遍用例，看日志输出 | 理解请求流程 |
| 3 | 尝试新增一个用例（比如报表模块） | 掌握用例编写 |
| 4 | 学习Allure报告集成 | 简历加分项 |
| 5 | 学习CI/CD集成（GitHub Actions） | 简历加分项 |
