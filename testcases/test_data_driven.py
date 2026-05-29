"""数据驱动测试用例

使用参数化覆盖多组数据：
- 登录参数化
- 支付参数化
- 会员充值参数化
- 订单状态参数化
- 搜索参数化
"""

import pytest
from utils.assertions import assert_status_code, assert_response_has_fields


@pytest.mark.data_driven
class TestDataDriven:
    """数据驱动测试"""

    # ========== 登录参数化 ==========

    @pytest.mark.parametrize("phone,password,expected_code", [
        ("13800000001", "test123456", 200),
        ("13800000002", "test123456", 200),
        ("13800000003", "test123456", 200),
    ], ids=["admin", "manager", "cashier"])
    def test_login_success_multiple_accounts(self, auth_api, phone, password, expected_code):
        """参数化测试：多个账号登录"""
        response = auth_api.login(phone, password)
        assert_status_code(response, expected_code)

    @pytest.mark.parametrize("phone,password,expected_msg", [
        ("", "test123456", "手机号不能为空"),
        ("13800000001", "", "密码不能为空"),
        ("", "", "手机号不能为空"),
        ("123", "test123456", "手机号格式"),
        ("13800000001", "123", "密码错误"),
    ], ids=["empty_phone", "empty_password", "both_empty", "short_phone", "wrong_password"])
    def test_login_failure_scenarios(self, auth_api, phone, password, expected_msg):
        """参数化测试：登录失败场景"""
        response = auth_api.login(phone, password)
        data = response.json()
        assert data.get("code") != 0
        assert expected_msg in data.get("msg", "")

    # ========== 支付方式参数化 ==========

    @pytest.mark.parametrize("pay_method,amount", [
        ("wechat", 10.00),
        ("alipay", 20.00),
        ("cash", 30.00),
        ("member_balance", 40.00),
    ], ids=["wechat", "alipay", "cash", "member_balance"])
    def test_create_payment_all_methods(self, payment_api, pay_method, amount):
        """参数化测试：所有支付方式"""
        response = payment_api.create_payment({
            "amount": amount,
            "payMethod": pay_method,
        })
        assert_status_code(response, 200)
        data = response.json()
        assert_response_has_fields(data["data"], ["paymentId", "amount", "status"])

    @pytest.mark.parametrize("amount,expected_success", [
        (0.01, True),      # 最小金额
        (1.00, True),      # 正常金额
        (99.99, True),     # 大金额
        (9999.99, True),   # 超大金额
        (0, False),        # 零金额
        (-10, False),      # 负数金额
    ], ids=["min", "normal", "large", "very_large", "zero", "negative"])
    def test_payment_amount_boundary(self, payment_api, amount, expected_success):
        """参数化测试：支付金额边界"""
        response = payment_api.create_payment({
            "amount": amount,
            "payMethod": "wechat",
        })
        data = response.json()
        if expected_success:
            assert data.get("code") in [0, 200]
        else:
            assert data.get("code") not in [0, 200]

    # ========== 会员充值参数化 ==========

    @pytest.mark.parametrize("amount,expected_bonus", [
        (50.00, 0),
        (100.00, 10.00),
        (200.00, 30.00),
        (300.00, 50.00),
        (500.00, 100.00),
        (1000.00, 200.00),
    ], ids=["50", "100", "200", "300", "500", "1000"])
    def test_member_recharge_tiers(self, member_api, amount, expected_bonus):
        """参数化测试：会员充值档位"""
        response = member_api.get_member_list(params={"pageSize": 1})
        data = response.json()
        if len(data["list"]) == 0:
            pytest.skip("没有可用的会员数据")
        member_id = data["list"][0]["id"]

        response = member_api.recharge(member_id, amount)
        assert_status_code(response, 200)
        recharge_data = response.json()["data"]
        assert recharge_data["amount"] == amount

    # ========== 订单状态参数化 ==========

    @pytest.mark.parametrize("status", [
        "pending",
        "confirmed",
        "completed",
        "cancelled",
        "refunding",
        "refunded",
    ], ids=["pending", "confirmed", "completed", "cancelled", "refunding", "refunded"])
    def test_order_list_by_status(self, order_api, status):
        """参数化测试：按状态查询订单"""
        response = order_api.get_order_list(params={"status": status})
        assert_status_code(response, 200)

    # ========== 搜索关键字参数化 ==========

    @pytest.mark.parametrize("keyword", [
        "ORD",
        "138",
        "测试",
        "奶茶",
        "张",
    ], ids=["order_no", "phone", "test", "product", "name"])
    def test_search_orders_keywords(self, order_api, keyword):
        """参数化测试：订单搜索关键字"""
        response = order_api.search_orders(keyword)
        assert_status_code(response, 200)

    @pytest.mark.parametrize("keyword", [
        "138",
        "张",
        "李",
        "会员",
        "VIP",
    ], ids=["phone", "name1", "name2", "member", "vip"])
    def test_search_members_keywords(self, member_api, keyword):
        """参数化测试：会员搜索关键字"""
        response = member_api.search_member(keyword)
        assert_status_code(response, 200)

    # ========== 商品分类参数化 ==========

    @pytest.mark.parametrize("category", [
        "奶茶系列",
        "果茶系列",
        "小食系列",
        "咖啡系列",
    ], ids=["milk_tea", "fruit_tea", "snack", "coffee"])
    def test_product_list_by_category(self, product_api, category):
        """参数化测试：按分类查询商品"""
        response = product_api.get_product_list(params={"category": category})
        assert_status_code(response, 200)

    # ========== 商品状态参数化 ==========

    @pytest.mark.parametrize("status", [
        "on",
        "off",
    ], ids=["on_shelf", "off_shelf"])
    def test_product_list_by_status(self, product_api, status):
        """参数化测试：按状态查询商品"""
        response = product_api.get_product_list(params={"status": status})
        assert_status_code(response, 200)

    # ========== 门店状态参数化 ==========

    @pytest.mark.parametrize("status", [
        "open",
        "closed",
    ], ids=["open", "closed"])
    def test_store_list_by_status(self, store_api, status):
        """参数化测试：按状态查询门店"""
        response = store_api.get_store_list(params={"status": status})
        assert_status_code(response, 200)

    # ========== 会员等级参数化 ==========

    @pytest.mark.parametrize("level", [
        "normal",
        "silver",
        "gold",
        "diamond",
    ], ids=["normal", "silver", "gold", "diamond"])
    def test_member_list_by_level(self, member_api, level):
        """参数化测试：按等级查询会员"""
        response = member_api.get_member_list(params={"level": level})
        assert_status_code(response, 200)

    # ========== 日期范围参数化 ==========

    @pytest.mark.parametrize("days", [
        1,
        7,
        30,
        90,
    ], ids=["1_day", "7_days", "30_days", "90_days"])
    def test_order_statistics_by_days(self, order_api, days):
        """参数化测试：按天数查询订单统计"""
        from datetime import datetime, timedelta
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

        response = order_api.get_order_statistics(params={
            "startDate": start_date,
            "endDate": end_date,
        })
        assert_status_code(response, 200)

    # ========== 分页参数化 ==========

    @pytest.mark.parametrize("page,page_size", [
        (1, 10),
        (1, 20),
        (1, 50),
        (2, 10),
        (5, 10),
    ], ids=["p1_s10", "p1_s20", "p1_s50", "p2_s10", "p5_s10"])
    def test_order_list_pagination(self, order_api, page, page_size):
        """参数化测试：订单列表分页"""
        response = order_api.get_order_list(params={"page": page, "pageSize": page_size})
        assert_status_code(response, 200)
        data = response.json()
        assert len(data["list"]) <= page_size

    # ========== 排序参数化 ==========

    @pytest.mark.parametrize("sort_by,sort_order", [
        ("createTime", "desc"),
        ("createTime", "asc"),
        ("amount", "desc"),
        ("amount", "asc"),
    ], ids=["time_desc", "time_asc", "amount_desc", "amount_asc"])
    def test_order_list_sorting(self, order_api, sort_by, sort_order):
        """参数化测试：订单列表排序"""
        response = order_api.get_order_list(params={
            "sortBy": sort_by,
            "sortOrder": sort_order,
        })
        assert_status_code(response, 200)

    # ========== 退款原因参数化 ==========

    @pytest.mark.parametrize("reason", [
        "顾客要求退款",
        "商品质量问题",
        "配送延迟",
        "重复支付",
        "其他原因",
    ], ids=["customer", "quality", "delivery", "duplicate", "other"])
    def test_refund_reasons(self, payment_api, reason):
        """参数化测试：退款原因"""
        # 先创建支付单
        create_resp = payment_api.create_payment({
            "amount": 10.00,
            "payMethod": "wechat",
        })
        if create_resp.status_code == 200:
            payment_id = create_resp.json()["data"]["paymentId"]
            response = payment_api.refund(payment_id, 10.00, reason)
            assert_status_code(response, 200)

    # ========== 会员标签参数化 ==========

    @pytest.mark.parametrize("tag", [
        "VIP客户",
        "高频消费",
        "新客户",
        "流失风险",
        "活跃用户",
    ], ids=["vip", "high_freq", "new", "churn", "active"])
    def test_member_tags(self, member_api, tag):
        """参数化测试：会员标签"""
        response = member_api.get_member_list(params={"pageSize": 1})
        data = response.json()
        if len(data["list"]) == 0:
            pytest.skip("没有可用的会员数据")
        member_id = data["list"][0]["id"]

        response = member_api.add_member_tag(member_id, tag)
        assert_status_code(response, 200)

    # ========== 商品规格参数化 ==========

    @pytest.mark.parametrize("spec_name,spec_values", [
        ("温度", ["热", "常温", "冰"]),
        ("甜度", ["全糖", "半糖", "少糖", "无糖"]),
        ("杯型", ["中杯", "大杯", "超大杯"]),
    ], ids=["temperature", "sweetness", "cup_size"])
    def test_product_specs(self, product_api, spec_name, spec_values):
        """参数化测试：商品规格"""
        response = product_api.get_product_list(params={"pageSize": 1})
        data = response.json()
        if len(data["list"]) == 0:
            pytest.skip("没有可用的商品数据")
        product_id = data["list"][0]["id"]

        response = product_api.add_product_spec(product_id, {
            "name": spec_name,
            "values": spec_values
        })
        assert_status_code(response, 200)
