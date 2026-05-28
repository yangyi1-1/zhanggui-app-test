"""通用测试 Fixtures

提供可复用的测试数据和工具函数。
"""

import pytest
from utils.helpers import generate_phone, generate_order_no


@pytest.fixture
def random_phone():
    """生成随机手机号"""
    return generate_phone()


@pytest.fixture
def random_order_no():
    """生成随机订单号"""
    return generate_order_no()


@pytest.fixture
def sample_member_data(test_data):
    """示例会员数据（带随机手机号）"""
    data = test_data["member"]["create"][0].copy()
    data["phone"] = generate_phone()
    return data


@pytest.fixture
def sample_product_data(test_data):
    """示例商品数据"""
    data = test_data["product"]["create"][0].copy()
    data["storeId"] = "STORE_001"
    return data
