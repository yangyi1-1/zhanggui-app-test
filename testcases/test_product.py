"""商品模块测试用例

覆盖掌柜APP商品管理功能：
- 商品分类CRUD
- 商品列表查询
- 商品详情查看
- 商品创建/更新/删除
- 商品上下架
- 批量操作
- 库存管理
- 商品规格
- 商品标签
- 商品排序
- 商品图片
- 商品统计
- 商品搜索
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

    def test_create_duplicate_category(self, product_api, test_data):
        """测试重复分类名称"""
        category_data = test_data["product"]["categories"][0]
        # 第一次创建
        product_api.create_category(category_data)
        # 第二次创建
        response = product_api.create_category(category_data)
        # 可能成功或失败，取决于业务规则
        assert response.status_code in [200, 400]

    def test_delete_nonexistent_category(self, product_api):
        """测试删除不存在的分类"""
        response = product_api.delete_category("CAT_999")
        assert_status_code(response, 404)

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

    def test_get_product_list_with_pagination(self, product_api):
        """测试商品列表分页"""
        response = product_api.get_product_list(params={"page": 1, "pageSize": 5})
        assert_status_code(response, 200)
        data = response.json()
        assert_pagination(data)
        assert len(data["list"]) <= 5

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

    def test_update_product_status_invalid(self, product_api):
        """测试无效商品状态"""
        response = product_api.get_product_list(params={"pageSize": 1})
        data = response.json()
        if len(data["list"]) == 0:
            pytest.skip("没有可用的商品数据")
        product_id = data["list"][0]["id"]

        response = product_api.update_product_status(product_id, "invalid")
        data = response.json()
        assert data.get("code") != 0, "无效状态应失败"

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

    def test_create_product_missing_fields(self, product_api):
        """测试缺少必填字段"""
        response = product_api.create_product({"name": "测试商品"})
        data = response.json()
        assert data.get("code") != 0, "缺少必填字段应失败"

    def test_create_product_invalid_price(self, product_api, test_data):
        """测试无效价格"""
        product_data = test_data["product"]["create"][0].copy()
        product_data["storeId"] = "STORE_001"
        product_data["price"] = -10.00
        response = product_api.create_product(product_data)
        data = response.json()
        assert data.get("code") != 0, "负价格应失败"

    def test_delete_nonexistent_product(self, product_api):
        """测试删除不存在的商品"""
        response = product_api.delete_product("PROD_999")
        assert_status_code(response, 404)

    def test_update_nonexistent_product(self, product_api):
        """测试更新不存在的商品"""
        response = product_api.update_product("PROD_999", {"name": "测试"})
        assert_status_code(response, 404)

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

    def test_batch_update_empty_list(self, product_api):
        """测试空列表批量操作"""
        response = product_api.batch_update_products([], "off_shelf")
        data = response.json()
        assert data.get("code") != 0, "空列表应失败"

    # ========== 库存管理 ==========

    def test_get_product_stock(self, product_api):
        """测试获取商品库存"""
        response = product_api.get_product_list(params={"pageSize": 1})
        data = response.json()
        if len(data["list"]) == 0:
            pytest.skip("没有可用的商品数据")
        product_id = data["list"][0]["id"]

        response = product_api.get_product_stock(product_id)
        assert_status_code(response, 200)
        data = response.json()
        assert "quantity" in data["data"]

    @pytest.mark.regression
    def test_update_product_stock(self, product_api):
        """测试更新商品库存"""
        response = product_api.get_product_list(params={"pageSize": 1})
        data = response.json()
        if len(data["list"]) == 0:
            pytest.skip("没有可用的商品数据")
        product_id = data["list"][0]["id"]

        response = product_api.update_product_stock(product_id, 100)
        assert_status_code(response, 200)

    def test_update_product_stock_negative(self, product_api):
        """测试负数库存"""
        response = product_api.get_product_list(params={"pageSize": 1})
        data = response.json()
        if len(data["list"]) == 0:
            pytest.skip("没有可用的商品数据")
        product_id = data["list"][0]["id"]

        response = product_api.update_product_stock(product_id, -10)
        data = response.json()
        assert data.get("code") != 0, "负数库存应失败"

    # ========== 商品规格 ==========

    def test_get_product_specs(self, product_api):
        """测试获取商品规格"""
        response = product_api.get_product_list(params={"pageSize": 1})
        data = response.json()
        if len(data["list"]) == 0:
            pytest.skip("没有可用的商品数据")
        product_id = data["list"][0]["id"]

        response = product_api.get_product_specs(product_id)
        assert_status_code(response, 200)
        data = response.json()
        assert isinstance(data["data"], list)

    @pytest.mark.regression
    def test_add_product_spec(self, product_api, test_data):
        """测试添加商品规格"""
        product_data = test_data["product"]["create"][0].copy()
        product_data["storeId"] = "STORE_001"
        create_resp = product_api.create_product(product_data)
        assert_status_code(create_resp, 200)
        product_id = create_resp.json()["data"]["id"]

        response = product_api.add_product_spec(product_id, {
            "name": "温度",
            "values": ["热", "常温", "冰"]
        })
        assert_status_code(response, 200)

        # 清理
        product_api.delete_product(product_id)

    # ========== 商品标签 ==========

    def test_get_product_tags(self, product_api):
        """测试获取商品标签"""
        response = product_api.get_product_list(params={"pageSize": 1})
        data = response.json()
        if len(data["list"]) == 0:
            pytest.skip("没有可用的商品数据")
        product_id = data["list"][0]["id"]

        response = product_api.get_product_tags(product_id)
        assert_status_code(response, 200)
        data = response.json()
        assert isinstance(data["data"], list)

    @pytest.mark.regression
    def test_add_product_tag(self, product_api):
        """测试添加商品标签"""
        response = product_api.get_product_list(params={"pageSize": 1})
        data = response.json()
        if len(data["list"]) == 0:
            pytest.skip("没有可用的商品数据")
        product_id = data["list"][0]["id"]

        response = product_api.add_product_tag(product_id, "热销")
        assert_status_code(response, 200)

    # ========== 商品排序 ==========

    @pytest.mark.regression
    def test_update_product_sort(self, product_api):
        """测试更新商品排序"""
        response = product_api.get_product_list(params={"pageSize": 1})
        data = response.json()
        if len(data["list"]) == 0:
            pytest.skip("没有可用的商品数据")
        product_id = data["list"][0]["id"]

        response = product_api.update_product_sort(product_id, 1)
        assert_status_code(response, 200)

    # ========== 商品图片 ==========

    @pytest.mark.regression
    def test_upload_product_image(self, product_api):
        """测试上传商品图片"""
        response = product_api.get_product_list(params={"pageSize": 1})
        data = response.json()
        if len(data["list"]) == 0:
            pytest.skip("没有可用的商品数据")
        product_id = data["list"][0]["id"]

        response = product_api.upload_product_image(product_id, {
            "url": "https://example.com/image.jpg",
            "type": "main"
        })
        assert_status_code(response, 200)

    # ========== 商品统计 ==========

    def test_get_product_statistics(self, product_api):
        """测试获取商品统计"""
        response = product_api.get_product_statistics()
        assert_status_code(response, 200)
        data = response.json()
        assert_response_has_fields(data["data"], [
            "totalProducts", "onShelfProducts", "offShelfProducts"
        ])

    # ========== 商品搜索 ==========

    def test_search_products(self, product_api):
        """测试搜索商品"""
        response = product_api.search_products("奶茶")
        assert_status_code(response, 200)

    def test_search_products_not_found(self, product_api):
        """测试搜索不存在的商品"""
        response = product_api.search_products("不存在的商品XYZ")
        assert_status_code(response, 200)
        data = response.json()
        assert len(data["list"]) == 0

    def test_search_products_empty_keyword(self, product_api):
        """测试空关键字搜索"""
        response = product_api.search_products("")
        # 空搜索可能返回全部或报错
        assert response.status_code in [200, 400]
