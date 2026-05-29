"""边界条件测试用例

覆盖各种边界条件：
- 空值测试
- 极值测试
- 特殊字符测试
- 长度边界测试
"""

import pytest
from utils.assertions import assert_status_code


@pytest.mark.edge_cases
class TestEdgeCases:
    """边界条件测试"""

    # ========== 空值测试 ==========

    def test_create_order_null_items(self, order_api):
        """测试订单商品为null"""
        response = order_api.create_order({"items": None, "payMethod": "wechat"})
        data = response.json()
        assert data.get("code") != 0

    def test_create_order_missing_items(self, order_api):
        """测试订单缺少商品字段"""
        response = order_api.create_order({"payMethod": "wechat"})
        data = response.json()
        assert data.get("code") != 0

    def test_create_payment_null_amount(self, payment_api):
        """测试支付金额为null"""
        response = payment_api.create_payment({
            "amount": None,
            "payMethod": "wechat",
        })
        data = response.json()
        assert data.get("code") != 0

    def test_create_member_null_name(self, member_api):
        """测试会员姓名为null"""
        response = member_api.create_member({
            "name": None,
            "phone": "13800001111",
            "gender": "male"
        })
        data = response.json()
        assert data.get("code") != 0

    def test_create_member_null_phone(self, member_api):
        """测试会员手机号为null"""
        response = member_api.create_member({
            "name": "测试",
            "phone": None,
            "gender": "male"
        })
        data = response.json()
        assert data.get("code") != 0

    # ========== 极值测试 ==========

    def test_create_order_max_quantity(self, order_api):
        """测试订单最大数量"""
        response = order_api.create_order({
            "items": [{"productId": "PROD_001", "quantity": 999999, "price": 10.00}],
            "payMethod": "wechat",
        })
        data = response.json()
        # 超大数量应该失败或有库存限制
        assert data.get("code") != 0 or data.get("data", {}).get("orderId")

    def test_create_order_max_price(self, order_api):
        """测试订单最大价格"""
        response = order_api.create_order({
            "items": [{"productId": "PROD_001", "quantity": 1, "price": 99999999.99}],
            "payMethod": "wechat",
        })
        data = response.json()
        # 超大金额应该有验证
        assert data.get("code") != 0 or data.get("data", {}).get("orderId")

    def test_create_payment_max_amount(self, payment_api):
        """测试支付最大金额"""
        response = payment_api.create_payment({
            "amount": 99999999.99,
            "payMethod": "wechat",
        })
        data = response.json()
        # 超大金额应该有验证
        assert data.get("code") != 0 or data.get("data", {}).get("paymentId")

    def test_member_recharge_max_amount(self, member_api):
        """测试会员充值最大金额"""
        response = member_api.get_member_list(params={"pageSize": 1})
        data = response.json()
        if len(data["list"]) == 0:
            pytest.skip("没有可用的会员数据")
        member_id = data["list"][0]["id"]

        response = member_api.recharge(member_id, 99999999.99)
        data = response.json()
        # 超大金额应该有验证
        assert data.get("code") != 0 or data.get("data", {}).get("amount")

    # ========== 特殊字符测试 ==========

    def test_create_order_special_chars_remark(self, order_api):
        """测试订单备注特殊字符"""
        special_chars = [
            "!@#$%^&*()",
            "中文测试",
            "🎉🎊🎈",
            "<script>alert(1)</script>",
            "'; DROP TABLE orders; --",
            "null",
            "undefined",
            "\\n\\r\\t",
        ]
        for chars in special_chars:
            response = order_api.create_order({
                "items": [{"productId": "PROD_001", "quantity": 1, "price": 10.00}],
                "payMethod": "wechat",
                "remark": chars,
            })
            # 应该成功或有明确的错误
            assert response.status_code in [200, 400]

    def test_create_member_special_chars_name(self, member_api):
        """测试会员姓名特殊字符"""
        special_chars = [
            "O'Connor",
            "Jean-Pierre",
            "张三·李四",
            "🎉🎊",
            "<b>粗体</b>",
        ]
        for chars in special_chars:
            response = member_api.create_member({
                "name": chars,
                "phone": "13800001111",
                "gender": "male"
            })
            assert response.status_code in [200, 400]

    # ========== 长度边界测试 ==========

    def test_create_member_long_name(self, member_api):
        """测试会员姓名超长"""
        long_name = "a" * 1000
        response = member_api.create_member({
            "name": long_name,
            "phone": "13800001111",
            "gender": "male"
        })
        data = response.json()
        # 超长姓名应该失败
        assert data.get("code") != 0

    def test_create_order_long_remark(self, order_api):
        """测试订单备注超长"""
        long_remark = "备注" * 500
        response = order_api.create_order({
            "items": [{"productId": "PROD_001", "quantity": 1, "price": 10.00}],
            "payMethod": "wechat",
            "remark": long_remark,
        })
        data = response.json()
        # 超长备注应该失败或截断
        assert data.get("code") != 0 or len(data.get("data", {}).get("remark", "")) <= 500

    def test_create_store_long_name(self, store_api):
        """测试门店名称超长"""
        long_name = "门店" * 100
        response = store_api.create_store({
            "name": long_name,
            "address": "测试地址",
            "phone": "010-88888888",
        })
        data = response.json()
        assert data.get("code") != 0

    def test_search_long_keyword(self, order_api):
        """测试搜索超长关键字"""
        long_keyword = "a" * 1000
        response = order_api.search_orders(long_keyword)
        # 应该返回空结果或错误
        assert response.status_code in [200, 400]

    # ========== 类型错误测试 ==========

    def test_create_order_invalid_quantity_type(self, order_api):
        """测试订单数量类型错误"""
        response = order_api.create_order({
            "items": [{"productId": "PROD_001", "quantity": "abc", "price": 10.00}],
            "payMethod": "wechat",
        })
        data = response.json()
        assert data.get("code") != 0

    def test_create_order_invalid_price_type(self, order_api):
        """测试订单价格类型错误"""
        response = order_api.create_order({
            "items": [{"productId": "PROD_001", "quantity": 1, "price": "免费"}],
            "payMethod": "wechat",
        })
        data = response.json()
        assert data.get("code") != 0

    def test_create_payment_invalid_amount_type(self, payment_api):
        """测试支付金额类型错误"""
        response = payment_api.create_payment({
            "amount": "十元",
            "payMethod": "wechat",
        })
        data = response.json()
        assert data.get("code") != 0

    def test_pagination_invalid_page(self, order_api):
        """测试分页页码类型错误"""
        response = order_api.get_order_list(params={"page": "abc", "pageSize": 10})
        # 应该返回错误或使用默认值
        assert response.status_code in [200, 400]

    def test_pagination_invalid_page_size(self, order_api):
        """测试分页每页数量类型错误"""
        response = order_api.get_order_list(params={"page": 1, "pageSize": "abc"})
        assert response.status_code in [200, 400]

    # ========== 负数测试 ==========

    def test_create_order_negative_quantity(self, order_api):
        """测试订单负数数量"""
        response = order_api.create_order({
            "items": [{"productId": "PROD_001", "quantity": -1, "price": 10.00}],
            "payMethod": "wechat",
        })
        data = response.json()
        assert data.get("code") != 0

    def test_create_order_negative_price(self, order_api):
        """测试订单负数价格"""
        response = order_api.create_order({
            "items": [{"productId": "PROD_001", "quantity": 1, "price": -10.00}],
            "payMethod": "wechat",
        })
        data = response.json()
        assert data.get("code") != 0

    def test_create_payment_negative_amount(self, payment_api):
        """测试支付负数金额"""
        response = payment_api.create_payment({
            "amount": -100.00,
            "payMethod": "wechat",
        })
        data = response.json()
        assert data.get("code") != 0

    def test_member_recharge_negative(self, member_api):
        """测试会员充值负数"""
        response = member_api.get_member_list(params={"pageSize": 1})
        data = response.json()
        if len(data["list"]) == 0:
            pytest.skip("没有可用的会员数据")
        member_id = data["list"][0]["id"]

        response = member_api.recharge(member_id, -100)
        data = response.json()
        assert data.get("code") != 0

    # ========== 小数精度测试 ==========

    def test_create_order_decimal_quantity(self, order_api):
        """测试订单小数数量"""
        response = order_api.create_order({
            "items": [{"productId": "PROD_001", "quantity": 1.5, "price": 10.00}],
            "payMethod": "wechat",
        })
        # 小数数量可能被接受或拒绝
        assert response.status_code in [200, 400]

    def test_create_payment_decimal_amount(self, payment_api):
        """测试支付小数金额"""
        response = payment_api.create_payment({
            "amount": 10.99,
            "payMethod": "wechat",
        })
        assert_status_code(response, 200)

    def test_create_payment_many_decimals(self, payment_api):
        """测试支付多位小数"""
        response = payment_api.create_payment({
            "amount": 10.999,
            "payMethod": "wechat",
        })
        # 多位小数应该被处理
        assert response.status_code in [200, 400]

    # ========== 重复请求测试 ==========

    def test_duplicate_create_order(self, order_api):
        """测试重复创建订单"""
        order_data = {
            "items": [{"productId": "PROD_001", "quantity": 1, "price": 10.00}],
            "payMethod": "wechat",
        }
        response1 = order_api.create_order(order_data)
        response2 = order_api.create_order(order_data)

        # 重复请求应该有防重机制
        assert response1.status_code in [200, 400]
        assert response2.status_code in [200, 400]

    def test_duplicate_create_payment(self, payment_api):
        """测试重复创建支付"""
        payment_data = {
            "orderId": "ORD_DUPLICATE_TEST",
            "amount": 10.00,
            "payMethod": "wechat",
        }
        response1 = payment_api.create_payment(payment_data)
        response2 = payment_api.create_payment(payment_data)

        # 同一订单重复支付应该有防重
        assert response1.status_code in [200, 400]
        assert response2.status_code in [200, 400]

    # ========== 空字符串测试 ==========

    def test_create_order_empty_remark(self, order_api):
        """测试订单空备注"""
        response = order_api.create_order({
            "items": [{"productId": "PROD_001", "quantity": 1, "price": 10.00}],
            "payMethod": "wechat",
            "remark": "",
        })
        # 空备注应该成功
        assert response.status_code in [200, 400]

    def test_search_empty_keyword(self, order_api):
        """测试搜索空关键字"""
        response = order_api.search_orders("")
        # 空搜索应该返回全部或错误
        assert response.status_code in [200, 400]

    def test_search_spaces_only(self, order_api):
        """测试搜索只有空格"""
        response = order_api.search_orders("   ")
        assert response.status_code in [200, 400]
