"""订单模块测试用例

覆盖掌柜APP订单管理功能：
- 订单列表查询（分页、筛选、搜索）
- 订单详情查看
- 订单创建
- 订单状态流转（确认→完成、取消）
- 订单退款
- 订单商品明细
- 订单备注
- 批量操作
- 订单统计
- 订单导出
"""

import pytest
from utils.assertions import assert_status_code, assert_response_has_fields, assert_pagination
from utils.helpers import generate_order_no


@pytest.mark.order
class TestOrder:
    """订单模块测试"""

    # ========== 订单列表 ==========

    @pytest.mark.smoke
    def test_get_order_list(self, order_api):
        """测试获取订单列表"""
        response = order_api.get_order_list()
        assert_status_code(response, 200)
        data = response.json()
        assert_pagination(data)

    def test_get_order_list_with_pagination(self, order_api):
        """测试订单列表分页"""
        response = order_api.get_order_list(params={"page": 1, "pageSize": 10})
        assert_status_code(response, 200)
        data = response.json()
        assert_pagination(data)
        assert len(data["list"]) <= 10

    def test_get_order_list_filter_by_status(self, order_api):
        """测试按状态筛选订单"""
        for status in ["pending", "confirmed", "completed", "cancelled"]:
            response = order_api.get_order_list(params={"status": status})
            assert_status_code(response, 200)

    def test_get_order_list_filter_by_date(self, order_api):
        """测试按日期筛选订单"""
        from utils.helpers import get_current_date
        response = order_api.get_order_list(params={
            "startDate": get_current_date(),
            "endDate": get_current_date(),
        })
        assert_status_code(response, 200)

    def test_search_orders(self, order_api):
        """测试搜索订单"""
        response = order_api.search_orders("ORD")
        assert_status_code(response, 200)

    # ========== 订单详情 ==========

    @pytest.mark.smoke
    def test_get_order_detail(self, order_api):
        """测试获取订单详情"""
        response = order_api.get_order_list(params={"pageSize": 1})
        data = response.json()
        if len(data["list"]) == 0:
            pytest.skip("没有可用的订单数据")
        order_id = data["list"][0]["id"]
        response = order_api.get_order_detail(order_id)
        assert_status_code(response, 200)
        detail = response.json()
        assert_response_has_fields(detail["data"], [
            "id", "orderNo", "status", "totalAmount", "items", "createTime"
        ])

    def test_get_nonexistent_order(self, order_api):
        """测试获取不存在的订单"""
        response = order_api.get_order_detail("ORD_999999")
        assert_status_code(response, 404)

    # ========== 订单商品明细 ==========

    def test_get_order_items(self, order_api):
        """测试获取订单商品明细"""
        response = order_api.get_order_list(params={"pageSize": 1})
        data = response.json()
        if len(data["list"]) == 0:
            pytest.skip("没有可用的订单数据")
        order_id = data["list"][0]["id"]
        response = order_api.get_order_items(order_id)
        assert_status_code(response, 200)
        items = response.json()["data"]
        assert isinstance(items, list)
        if len(items) > 0:
            assert_response_has_fields(items[0], [
                "productName", "quantity", "price", "subtotal"
            ])

    # ========== 订单状态流转 ==========

    @pytest.mark.regression
    def test_order_status_flow_confirm(self, order_api):
        """测试订单确认"""
        response = order_api.get_order_list(params={"status": "pending", "pageSize": 1})
        data = response.json()
        if len(data["list"]) == 0:
            pytest.skip("没有待确认的订单")
        order_id = data["list"][0]["id"]
        response = order_api.confirm_order(order_id)
        assert_status_code(response, 200)

    @pytest.mark.regression
    def test_order_status_flow_complete(self, order_api):
        """测试订单完成"""
        response = order_api.get_order_list(params={"status": "confirmed", "pageSize": 1})
        data = response.json()
        if len(data["list"]) == 0:
            pytest.skip("没有已确认的订单")
        order_id = data["list"][0]["id"]
        response = order_api.complete_order(order_id)
        assert_status_code(response, 200)

    @pytest.mark.regression
    def test_order_cancel(self, order_api):
        """测试取消订单"""
        response = order_api.get_order_list(params={"status": "pending", "pageSize": 1})
        data = response.json()
        if len(data["list"]) == 0:
            pytest.skip("没有待确认的订单")
        order_id = data["list"][0]["id"]
        response = order_api.cancel_order(order_id, "用户主动取消")
        assert_status_code(response, 200)

    # ========== 订单退款 ==========

    @pytest.mark.regression
    def test_order_refund(self, order_api, test_data):
        """测试订单退款"""
        response = order_api.get_order_list(params={"status": "completed", "pageSize": 1})
        data = response.json()
        if len(data["list"]) == 0:
            pytest.skip("没有已完成的订单")
        order_id = data["list"][0]["id"]
        refund_data = test_data["order"]["refund"]
        response = order_api.refund_order(order_id, refund_data)
        assert_status_code(response, 200)

    # ========== 订单备注 ==========

    def test_update_order_remark(self, order_api):
        """测试更新订单备注"""
        response = order_api.get_order_list(params={"pageSize": 1})
        data = response.json()
        if len(data["list"]) == 0:
            pytest.skip("没有可用的订单数据")
        order_id = data["list"][0]["id"]
        response = order_api.update_order_remark(order_id, "测试备注")
        assert_status_code(response, 200)

    # ========== 批量操作 ==========

    @pytest.mark.regression
    def test_batch_confirm_orders(self, order_api):
        """测试批量确认订单"""
        response = order_api.get_order_list(params={"status": "pending", "pageSize": 3})
        data = response.json()
        if len(data["list"]) == 0:
            pytest.skip("没有待确认的订单")
        order_ids = [o["id"] for o in data["list"]]
        response = order_api.batch_confirm_orders(order_ids)
        assert_status_code(response, 200)

    @pytest.mark.regression
    def test_batch_cancel_orders(self, order_api):
        """测试批量取消订单"""
        response = order_api.get_order_list(params={"status": "pending", "pageSize": 3})
        data = response.json()
        if len(data["list"]) == 0:
            pytest.skip("没有待确认的订单")
        order_ids = [o["id"] for o in data["list"]]
        response = order_api.batch_cancel_orders(order_ids, "批量取消测试")
        assert_status_code(response, 200)

    # ========== 订单统计 ==========

    def test_get_order_statistics(self, order_api):
        """测试获取订单统计"""
        response = order_api.get_order_statistics()
        assert_status_code(response, 200)
        data = response.json()
        assert_response_has_fields(data["data"], [
            "todayOrders", "todayRevenue", "totalOrders", "totalRevenue"
        ])

    def test_get_order_statistics_by_date(self, order_api):
        """测试按日期获取订单统计"""
        from utils.helpers import get_current_date
        response = order_api.get_order_statistics(params={
            "startDate": get_current_date(),
            "endDate": get_current_date(),
        })
        assert_status_code(response, 200)

    # ========== 订单导出 ==========

    def test_export_orders(self, order_api):
        """测试导出订单"""
        response = order_api.export_orders()
        assert_status_code(response, 200)

    # ========== 订单操作日志 ==========

    def test_get_order_log(self, order_api):
        """测试获取订单操作日志"""
        response = order_api.get_order_list(params={"pageSize": 1})
        data = response.json()
        if len(data["list"]) == 0:
            pytest.skip("没有可用的订单数据")
        order_id = data["list"][0]["id"]
        response = order_api.get_order_log(order_id)
        assert_status_code(response, 200)
        data = response.json()
        assert isinstance(data["data"], list)

    # ========== 边界测试 ==========

    def test_create_order_empty_items(self, order_api):
        """测试创建空商品订单"""
        response = order_api.create_order({"items": [], "payMethod": "wechat"})
        data = response.json()
        assert data.get("code") != 0, "空商品订单应创建失败"

    def test_create_order_zero_quantity(self, order_api):
        """测试创建数量为0的订单"""
        response = order_api.create_order({
            "items": [{"productId": "PROD_001", "quantity": 0, "price": 12.00}],
            "payMethod": "wechat",
        })
        data = response.json()
        assert data.get("code") != 0, "数量为0应创建失败"

    def test_create_order_negative_price(self, order_api):
        """测试创建负价格订单"""
        response = order_api.create_order({
            "items": [{"productId": "PROD_001", "quantity": 1, "price": -10.00}],
            "payMethod": "wechat",
        })
        data = response.json()
        assert data.get("code") != 0, "负价格应创建失败"

    def test_cancel_completed_order(self, order_api):
        """测试取消已完成的订单"""
        response = order_api.get_order_list(params={"status": "completed", "pageSize": 1})
        data = response.json()
        if len(data["list"]) == 0:
            pytest.skip("没有已完成的订单")
        order_id = data["list"][0]["id"]
        response = order_api.cancel_order(order_id, "测试取消")
        data = response.json()
        assert data.get("code") != 0, "已完成订单不能取消"
