"""门店模块测试用例

覆盖掌柜APP门店管理功能：
- 门店列表查询
- 门店详情查看
- 门店创建/更新/删除
- 门店状态切换
- 门店统计
"""

import pytest
from utils.assertions import assert_status_code, assert_response_has_fields, assert_pagination


@pytest.mark.store
class TestStore:
    """门店模块测试"""

    # ========== 门店列表 ==========

    @pytest.mark.smoke
    def test_get_store_list(self, store_api):
        """测试获取门店列表"""
        response = store_api.get_store_list()
        assert_status_code(response, 200)
        data = response.json()
        assert_pagination(data)
        assert len(data["list"]) > 0, "门店列表不应为空"

    def test_get_store_list_with_pagination(self, store_api):
        """测试门店列表分页"""
        response = store_api.get_store_list(params={"page": 1, "pageSize": 5})
        assert_status_code(response, 200)
        data = response.json()
        assert_pagination(data)
        assert len(data["list"]) <= 5

    def test_get_store_list_with_keyword(self, store_api):
        """测试门店列表关键字搜索"""
        response = store_api.get_store_list(params={"keyword": "奶茶"})
        assert_status_code(response, 200)
        data = response.json()
        assert_pagination(data)

    # ========== 门店详情 ==========

    @pytest.mark.smoke
    def test_get_store_detail(self, store_api, store_id):
        """测试获取门店详情"""
        response = store_api.get_store_detail(store_id)
        assert_status_code(response, 200)
        data = response.json()
        assert_response_has_fields(data["data"], [
            "id", "name", "address", "phone", "status", "businessHours"
        ])

    def test_get_nonexistent_store(self, store_api):
        """测试获取不存在的门店"""
        response = store_api.get_store_detail("STORE_999")
        assert_status_code(response, 404)

    # ========== 门店统计 ==========

    def test_get_store_stats(self, store_api, store_id):
        """测试获取门店统计数据"""
        response = store_api.get_store_stats(store_id)
        assert_status_code(response, 200)
        data = response.json()
        assert_response_has_fields(data["data"], [
            "todayOrders", "todayRevenue", "totalOrders", "totalRevenue"
        ])

    # ========== 门店状态 ==========

    @pytest.mark.regression
    def test_update_store_status(self, store_api, store_id):
        """测试更新门店状态"""
        response = store_api.update_store_status(store_id, "closed")
        assert_status_code(response, 200)
        # 恢复营业状态
        store_api.update_store_status(store_id, "open")

    # ========== 门店CRUD ==========

    @pytest.mark.regression
    def test_store_crud(self, store_api, test_data):
        """测试门店完整CRUD流程"""
        store_data = test_data["store"]["create"][0]

        # 创建
        response = store_api.create_store(store_data)
        assert_status_code(response, 200)
        created = response.json()
        store_id = created["data"]["id"]

        # 查看
        response = store_api.get_store_detail(store_id)
        assert_status_code(response, 200)
        detail = response.json()
        assert detail["data"]["name"] == store_data["name"]

        # 更新
        update_data = {"name": "更新后的门店名称"}
        response = store_api.update_store(store_id, update_data)
        assert_status_code(response, 200)

        # 删除
        response = store_api.delete_store(store_id)
        assert_status_code(response, 200)
