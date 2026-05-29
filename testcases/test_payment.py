"""支付模块测试用例

覆盖掌柜APP支付功能：
- 创建支付单
- 支付状态查询
- 支付回调模拟
- 退款
- 日结算数据
- 多支付方式测试
- 重复支付检查
- 支付统计
- 支付渠道
- 支付验证
- 支付关闭
"""

import pytest
from utils.assertions import assert_status_code, assert_response_has_fields, assert_pagination
from utils.helpers import get_current_date


@pytest.mark.payment
class TestPayment:
    """支付模块测试"""

    # ========== 支付单创建 ==========

    @pytest.mark.smoke
    def test_create_payment_wechat(self, payment_api):
        """测试创建微信支付单"""
        response = payment_api.create_payment({
            "amount": 42.00,
            "payMethod": "wechat",
        })
        assert_status_code(response, 200)
        data = response.json()
        assert_response_has_fields(data["data"], ["paymentId", "amount", "status"])

    @pytest.mark.smoke
    def test_create_payment_alipay(self, payment_api):
        """测试创建支付宝支付单"""
        response = payment_api.create_payment({
            "amount": 30.00,
            "payMethod": "alipay",
        })
        assert_status_code(response, 200)
        data = response.json()
        assert_response_has_fields(data["data"], ["paymentId", "amount", "status"])

    def test_create_payment_cash(self, payment_api):
        """测试创建现金支付单"""
        response = payment_api.create_payment({
            "amount": 15.00,
            "payMethod": "cash",
        })
        assert_status_code(response, 200)
        data = response.json()
        assert_response_has_fields(data["data"], ["paymentId", "amount", "status"])

    def test_create_payment_member_balance(self, payment_api):
        """测试会员余额支付"""
        response = payment_api.create_payment({
            "amount": 25.00,
            "payMethod": "member_balance",
            "memberId": "MEM_001",
        })
        assert_status_code(response, 200)
        data = response.json()
        assert_response_has_fields(data["data"], ["paymentId", "amount", "status"])

    # ========== 支付异常 ==========

    def test_create_payment_zero_amount(self, payment_api):
        """测试0元支付"""
        response = payment_api.create_payment({
            "amount": 0,
            "payMethod": "wechat",
        })
        data = response.json()
        assert data.get("code") != 0, "0元支付应失败"

    def test_create_payment_negative_amount(self, payment_api):
        """测试负数金额支付"""
        response = payment_api.create_payment({
            "amount": -10.00,
            "payMethod": "wechat",
        })
        data = response.json()
        assert data.get("code") != 0, "负数金额应失败"

    def test_create_payment_invalid_method(self, payment_api):
        """测试无效支付方式"""
        response = payment_api.create_payment({
            "amount": 10.00,
            "payMethod": "bitcoin",
        })
        data = response.json()
        assert data.get("code") != 0, "无效支付方式应失败"

    # ========== 支付状态 ==========

    @pytest.mark.smoke
    def test_get_payment_status(self, payment_api):
        """测试查询支付状态"""
        # 先创建支付单
        create_resp = payment_api.create_payment({
            "amount": 18.00,
            "payMethod": "wechat",
        })
        assert_status_code(create_resp, 200)
        payment_id = create_resp.json()["data"]["paymentId"]

        response = payment_api.get_payment_status(payment_id)
        assert_status_code(response, 200)
        data = response.json()
        assert data["data"]["status"] in ["pending", "paid", "failed"]

    # ========== 支付记录 ==========

    def test_get_payment_list(self, payment_api):
        """测试获取支付记录列表"""
        response = payment_api.get_payment_list()
        assert_status_code(response, 200)
        data = response.json()
        assert_pagination(data)

    def test_get_payment_list_by_date(self, payment_api):
        """测试按日期查询支付记录"""
        response = payment_api.get_payment_list(params={
            "startDate": get_current_date(),
            "endDate": get_current_date(),
        })
        assert_status_code(response, 200)

    def test_get_payment_list_by_method(self, payment_api):
        """测试按支付方式查询支付记录"""
        for method in ["wechat", "alipay", "cash"]:
            response = payment_api.get_payment_list(params={"payMethod": method})
            assert_status_code(response, 200)

    # ========== 退款 ==========

    @pytest.mark.regression
    def test_refund(self, payment_api):
        """测试退款"""
        # 先创建支付单
        create_resp = payment_api.create_payment({
            "amount": 36.00,
            "payMethod": "wechat",
        })
        assert_status_code(create_resp, 200)
        payment_id = create_resp.json()["data"]["paymentId"]

        response = payment_api.refund(payment_id, 36.00, "顾客要求退款")
        assert_status_code(response, 200)

    def test_partial_refund(self, payment_api):
        """测试部分退款"""
        create_resp = payment_api.create_payment({
            "amount": 50.00,
            "payMethod": "wechat",
        })
        assert_status_code(create_resp, 200)
        payment_id = create_resp.json()["data"]["paymentId"]

        response = payment_api.refund(payment_id, 20.00, "部分退款")
        assert_status_code(response, 200)

    def test_refund_exceed_amount(self, payment_api):
        """测试退款金额超过支付金额"""
        create_resp = payment_api.create_payment({
            "amount": 10.00,
            "payMethod": "wechat",
        })
        assert_status_code(create_resp, 200)
        payment_id = create_resp.json()["data"]["paymentId"]

        response = payment_api.refund(payment_id, 100.00, "超额退款")
        data = response.json()
        assert data.get("code") != 0, "超额退款应失败"

    # ========== 退款状态查询 ==========

    def test_get_refund_status(self, payment_api):
        """测试查询退款状态"""
        # 先创建支付并退款
        create_resp = payment_api.create_payment({
            "amount": 20.00,
            "payMethod": "wechat",
        })
        assert_status_code(create_resp, 200)
        payment_id = create_resp.json()["data"]["paymentId"]

        refund_resp = payment_api.refund(payment_id, 20.00, "测试退款")
        assert_status_code(refund_resp, 200)
        refund_id = refund_resp.json()["data"]["refundId"]

        response = payment_api.get_refund_status(refund_id)
        assert_status_code(response, 200)
        data = response.json()
        assert data["data"]["status"] in ["pending", "success", "failed"]

    # ========== 重复支付检查 ==========

    def test_check_duplicate_payment(self, payment_api):
        """测试检查重复支付"""
        response = payment_api.check_duplicate_payment("ORD_TEST_001")
        assert_status_code(response, 200)

    # ========== 支付统计 ==========

    def test_get_payment_statistics(self, payment_api):
        """测试获取支付统计"""
        response = payment_api.get_payment_statistics()
        assert_status_code(response, 200)
        data = response.json()
        assert_response_has_fields(data["data"], [
            "todayAmount", "todayCount", "totalAmount", "totalCount"
        ])

    def test_get_payment_statistics_by_date(self, payment_api):
        """测试按日期获取支付统计"""
        response = payment_api.get_payment_statistics(params={
            "startDate": get_current_date(),
            "endDate": get_current_date(),
        })
        assert_status_code(response, 200)

    # ========== 支付渠道 ==========

    def test_get_payment_channels(self, payment_api):
        """测试获取支付渠道列表"""
        response = payment_api.get_payment_channels()
        assert_status_code(response, 200)
        data = response.json()
        assert isinstance(data["data"], list)
        assert len(data["data"]) > 0

    # ========== 支付验证 ==========

    def test_verify_payment(self, payment_api):
        """测试验证支付结果"""
        create_resp = payment_api.create_payment({
            "amount": 15.00,
            "payMethod": "wechat",
        })
        assert_status_code(create_resp, 200)
        payment_id = create_resp.json()["data"]["paymentId"]

        response = payment_api.verify_payment(payment_id)
        assert_status_code(response, 200)

    # ========== 支付关闭 ==========

    def test_close_payment(self, payment_api):
        """测试关闭支付单"""
        create_resp = payment_api.create_payment({
            "amount": 25.00,
            "payMethod": "wechat",
        })
        assert_status_code(create_resp, 200)
        payment_id = create_resp.json()["data"]["paymentId"]

        response = payment_api.close_payment(payment_id, "超时未支付")
        assert_status_code(response, 200)

    # ========== 日结算 ==========

    def test_get_daily_settlement(self, payment_api, store_id):
        """测试获取日结算数据"""
        response = payment_api.get_daily_settlement(store_id, get_current_date())
        assert_status_code(response, 200)
        data = response.json()
        assert_response_has_fields(data["data"], [
            "totalAmount", "wechatAmount", "alipayAmount", "cashAmount", "orderCount"
        ])

    # ========== 边界测试 ==========

    def test_create_payment_decimal_amount(self, payment_api):
        """测试小数金额支付"""
        response = payment_api.create_payment({
            "amount": 9.99,
            "payMethod": "wechat",
        })
        assert_status_code(response, 200)

    def test_create_payment_large_amount(self, payment_api):
        """测试大额支付"""
        response = payment_api.create_payment({
            "amount": 99999.99,
            "payMethod": "wechat",
        })
        # 大额支付可能需要额外验证
        assert response.status_code in [200, 400]

    def test_refund_zero_amount(self, payment_api):
        """测试0元退款"""
        create_resp = payment_api.create_payment({
            "amount": 10.00,
            "payMethod": "wechat",
        })
        assert_status_code(create_resp, 200)
        payment_id = create_resp.json()["data"]["paymentId"]

        response = payment_api.refund(payment_id, 0, "测试0元退款")
        data = response.json()
        assert data.get("code") != 0, "0元退款应失败"

    def test_refund_negative_amount(self, payment_api):
        """测试负数退款"""
        create_resp = payment_api.create_payment({
            "amount": 10.00,
            "payMethod": "wechat",
        })
        assert_status_code(create_resp, 200)
        payment_id = create_resp.json()["data"]["paymentId"]

        response = payment_api.refund(payment_id, -5.00, "测试负数退款")
        data = response.json()
        assert data.get("code") != 0, "负数退款应失败"
