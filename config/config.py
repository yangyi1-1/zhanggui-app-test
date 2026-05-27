"""掌柜APP项目配置"""

# ========== 环境配置 ==========
ENV = "test"

# 各环境URL
ENV_CONFIG = {
    "test": {
        "base_url": "https://test-api.zhanggui.huameng.com",
        "web_url": "https://test.zhanggui.huameng.com",
    },
    "staging": {
        "base_url": "https://staging-api.zhanggui.huameng.com",
        "web_url": "https://staging.zhanggui.huameng.com",
    },
    "prod": {
        "base_url": "https://api.zhanggui.huameng.com",
        "web_url": "https://zhanggui.huameng.com",
    },
}

# 当前环境配置
BASE_URL = ENV_CONFIG[ENV]["base_url"]

# ========== 请求配置 ==========
TIMEOUT = 15

HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "X-Platform": "zhanggui-app",
    "X-Version": "3.2.1",
}

# ========== 测试账号 ==========
TEST_ACCOUNTS = {
    "admin": {
        "phone": "13800000001",
        "password": "test123456",
        "role": "admin",
    },
    "manager": {
        "phone": "13800000002",
        "password": "test123456",
        "role": "store_manager",
    },
    "cashier": {
        "phone": "13800000003",
        "password": "test123456",
        "role": "cashier",
    },
}

# ========== 门店配置 ==========
TEST_STORE_ID = "STORE_001"
TEST_MERCHANT_ID = "MERCHANT_001"
