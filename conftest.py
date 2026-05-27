"""pytest全局配置

管理测试生命周期：登录认证、Token管理、测试数据准备。
"""

import pytest
import yaml
import os
from api.auth_api import AuthAPI
from api.store_api import StoreAPI
from api.product_api import ProductAPI
from api.order_api import OrderAPI
from api.payment_api import PaymentAPI
from api.member_api import MemberAPI
from config.config import TEST_ACCOUNTS, TEST_STORE_ID
from utils.logger import logger


def pytest_addoption(parser):
    parser.addoption("--env", action="store", default="test", help="测试环境")
    parser.addoption("--base-url", action="store", default=None, help="API基础URL")


@pytest.fixture(scope="session")
def test_data():
    """加载测试数据"""
    data_file = os.path.join(os.path.dirname(__file__), "data", "test_data.yaml")
    with open(data_file, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="session")
def auth_api():
    """认证API实例"""
    return AuthAPI()


@pytest.fixture(scope="session")
def admin_token(auth_api):
    """管理员Token（session级复用）"""
    account = TEST_ACCOUNTS["admin"]
    response = auth_api.login(account["phone"], account["password"])
    data = response.json()
    token = data.get("data", {}).get("token", "mock_token_for_test")
    logger.info(f"管理员登录成功，Token: {token[:20]}...")
    yield token


@pytest.fixture(scope="session")
def api_client(admin_token):
    """带认证的通用API客户端"""
    from api.client import APIClient
    client = APIClient()
    client.set_token(admin_token)
    return client


@pytest.fixture(scope="session")
def store_api(admin_token):
    """门店API（已认证）"""
    api = StoreAPI()
    api.set_token(admin_token)
    return api


@pytest.fixture(scope="session")
def product_api(admin_token):
    """商品API（已认证）"""
    api = ProductAPI()
    api.set_token(admin_token)
    return api


@pytest.fixture(scope="session")
def order_api(admin_token):
    """订单API（已认证）"""
    api = OrderAPI()
    api.set_token(admin_token)
    return api


@pytest.fixture(scope="session")
def payment_api(admin_token):
    """支付API（已认证）"""
    api = PaymentAPI()
    api.set_token(admin_token)
    return api


@pytest.fixture(scope="session")
def member_api(admin_token):
    """会员API（已认证）"""
    api = MemberAPI()
    api.set_token(admin_token)
    return api


@pytest.fixture(scope="session")
def store_id():
    """测试门店ID"""
    return TEST_STORE_ID


def pytest_configure(config):
    logger.info("=" * 60)
    logger.info("掌柜APP 自动化测试开始")
    logger.info("=" * 60)


def pytest_sessionfinish(session, exitstatus):
    logger.info("=" * 60)
    logger.info(f"测试结束，退出码: {exitstatus}")
    logger.info("=" * 60)
