"""商品模块测试用例

覆盖掌柜APP商品管理功能：
- 商品分类CRUD
- 商品列表查询
- 商品详情查看
- 商品创建/更新/删除
- 商品上下架
- 批量操作
"""

import pytest
from utils.assertions import assert_status_code, assert_response_has_fields, assert_pagination


@pytest.mark.product
class TestProduct:
    """商品模块测试"""

    # ========== 分类测试 ==========

    @pytest.mark.smoke
    def test_get_category_list(self, product_api, store_id):
        """测试获取商品分类列表"""
        response = product_api.get_category_list(store_id)
        assert_status_code(response, 200)
        data = response.json()
        assert isinstance(data["data"], list)

    def test_category_crud(self, product_api, test_data):
        """测试分类完整CRUD流程"""
        category_data = test_data["product"]["categories"][0]

        # 创建
        response = product_api.create_category(category_data)
        assert_status_code(response, 200)
        category_id = response.json()["data"]["id"]

        # 更新
        response = product_api.update_category(category_id, {"name": "奶茶系列-已更新"})
        assert_status_code(response, 200)

        # 删除
        response = product_api.delete_category(category_id)
        assert_status_code(response, 200)

    # ========== 商品列表 ==========

    @pytest.mark.smoke
    def test_get_product_list(self, product_api):
        """测试获取商品列表"""
        response = product_api.get_product_list()
        assert_status_code(response, 200)
        data = response.json()
        assert_pagination(data)

    def test_get_product_list_by_category(self, product_api):
        """测试按分类筛选商品"""
        response = product_api.get_product_list(params={"category": "奶茶系列"})
        assert_status_code(response, 200)
        data = response.json()
        assert_pagination(data)

    def test_get_product_list_by_status(self, product_api):
        """测试按状态筛选商品"""
        response = product_api.get_product_list(params={"status": "on"})
        assert_status_code(response, 200)
        data = response.json()
        assert_pagination(data)

    # ========== 商品详情 ==========

    @pytest.mark.smoke
    def test_get_product_detail(self, product_api):
        """测试获取商品详情"""
        response = product_api.get_product_list(params={"pageSize": 1})
        data = response.json()
        if len(data["list"]) == 0:
            pytest.skip("没有可用的商品数据")
        product_id = data["list"][0]["id"]

        response = product_api.get_product_detail(product_id)
        assert_status_code(response, 200)
        data = response.json()
        assert_response_has_fields(data["data"], [
            "id", "name", "price", "category", "status", "description"
        ])

    def test_get_nonexistent_product(self, product_api):
        """测试获取不存在的商品"""
        response = product_api.get_product_detail("PROD_999")
        assert_status_code(response, 404)

    # ========== 商品上下架 ==========

    @pytest.mark.regression
    def test_product_on_off_shelf(self, product_api, test_data):
        """测试商品上下架"""
        product_data = test_data["product"]["create"][0].copy()
        product_data["storeId"] = "STORE_001"

        # 创建商品
        response = product_api.create_product(product_data)
        assert_status_code(response, 200)
        product_id = response.json()["data"]["id"]

        # 下架
        response = product_api.update_product_status(product_id, "off")
        assert_status_code(response, 200)

        # 上架
        response = product_api.update_product_status(product_id, "on")
        assert_status_code(response, 200)

        # 清理
        product_api.delete_product(product_id)

    # ========== 商品CRUD ==========

    @pytest.mark.regression
    def test_product_crud(self, product_api, test_data):
        """测试商品完整CRUD流程"""
        product_data = test_data["product"]["create"][1].copy()
        product_data["storeId"] = "STORE_001"

        # 创建
        response = product_api.create_product(product_data)
        assert_status_code(response, 200)
        product_id = response.json()["data"]["id"]

        # 查看
        response = product_api.get_product_detail(product_id)
        assert response.json()["data"]["name"] == product_data["name"]

        # 更新
        response = product_api.update_product(product_id, {"price": 20.00})
        assert_status_code(response, 200)

        # 删除
        response = product_api.delete_product(product_id)
        assert_status_code(response, 200)

    # ========== 批量操作 ==========

    @pytest.mark.regression
    def test_batch_update_products(self, product_api):
        """测试批量操作商品"""
        # 获取商品列表
        response = product_api.get_product_list(params={"pageSize": 3})
        data = response.json()
        if len(data["list"]) == 0:
            pytest.skip("没有可用的商品数据")
        product_ids = [p["id"] for p in data["list"]]

        response = product_api.batch_update_products(product_ids, "off_shelf")
        assert_status_code(response, 200)
