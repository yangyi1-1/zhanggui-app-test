"""并发测试用例

覆盖掌柜APP并发场景：
- 并发登录
- 并发下单
- 并发支付
- 并发库存扣减
- 并发会员充值
"""

import pytest
import threading
import time
from utils.assertions import assert_status_code


@pytest.mark.concurrency
class TestConcurrency:
    """并发测试"""

    # ========== 并发登录 ==========

    def test_concurrent_login(self, auth_api, test_data):
        """测试并发登录"""
        account = test_data["auth"]["valid_login"]
        results = []
        errors = []

        def login():
            try:
                response = auth_api.login(account["phone"], account["password"])
                results.append(response.status_code)
            except Exception as e:
                errors.append(str(e))

        # 创建10个并发线程
        threads = [threading.Thread(target=login) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # 验证结果
        assert len(errors) == 0, f"并发登录出现错误: {errors}"
        assert all(code == 200 for code in results), f"部分登录失败: {results}"

    def test_concurrent_login_same_account(self, auth_api, test_data):
        """测试同一账号并发登录"""
        account = test_data["auth"]["valid_login"]
        results = []

        def login():
            response = auth_api.login(account["phone"], account["password"])
            results.append(response.status_code)

        threads = [threading.Thread(target=login) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # 同一账号并发登录应该都能成功或部分被拒绝
        assert all(code in [200, 401, 429] for code in results)

    # ========== 并发下单 ==========

    def test_concurrent_create_order(self, order_api):
        """测试并发创建订单"""
        results = []
        errors = []

        def create_order():
            try:
                response = order_api.create_order({
                    "items": [{"productId": "PROD_001", "quantity": 1, "price": 12.00}],
                    "payMethod": "wechat",
                })
                results.append(response.status_code)
            except Exception as e:
                errors.append(str(e))

        threads = [threading.Thread(target=create_order) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0, f"并发下单出现错误: {errors}"
        # 并发下单应该都能成功或部分因库存不足失败
        assert all(code in [200, 400] for code in results)

    def test_concurrent_create_order_same_product(self, order_api):
        """测试并发下单同一商品（库存竞争）"""
        results = []

        def create_order():
            response = order_api.create_order({
                "items": [{"productId": "PROD_LIMITED", "quantity": 1, "price": 100.00}],
                "payMethod": "wechat",
            })
            results.append(response.json())

        threads = [threading.Thread(target=create_order) for _ in range(20)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # 验证不会超卖
        success_count = sum(1 for r in results if r.get("code") in [0, 200])
        # 如果库存有限，成功数不应超过库存数
        assert success_count <= 10, "可能存在超卖问题"

    # ========== 并发支付 ==========

    def test_concurrent_payment(self, payment_api):
        """测试并发支付"""
        results = []
        errors = []

        def create_payment():
            try:
                response = payment_api.create_payment({
                    "amount": 10.00,
                    "payMethod": "wechat",
                })
                results.append(response.status_code)
            except Exception as e:
                errors.append(str(e))

        threads = [threading.Thread(target=create_payment) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0, f"并发支付出现错误: {errors}"
        assert all(code == 200 for code in results)

    def test_concurrent_same_order_payment(self, payment_api):
        """测试同一订单并发支付（防重复支付）"""
        results = []

        def pay():
            response = payment_api.create_payment({
                "orderId": "ORD_CONCURRENT_TEST",
                "amount": 50.00,
                "payMethod": "wechat",
            })
            results.append(response.json())

        threads = [threading.Thread(target=pay) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # 同一订单应该只有一次支付成功
        success_count = sum(1 for r in results if r.get("code") in [0, 200])
        assert success_count <= 1, "同一订单重复支付"

    # ========== 并发库存扣减 ==========

    def test_concurrent_stock_deduction(self, product_api):
        """测试并发库存扣减"""
        results = []

        def deduct_stock():
            response = product_api.update_product_stock("PROD_001", -1)
            results.append(response.status_code)

        threads = [threading.Thread(target=deduct_stock) for _ in range(20)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # 并发扣减应该不会导致库存为负
        assert all(code in [200, 400] for code in results)

    # ========== 并发会员充值 ==========

    def test_concurrent_member_recharge(self, member_api):
        """测试并发会员充值"""
        results = []
        errors = []

        def recharge():
            try:
                response = member_api.recharge("MEM_001", 100.00)
                results.append(response.status_code)
            except Exception as e:
                errors.append(str(e))

        threads = [threading.Thread(target=recharge) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0, f"并发充值出现错误: {errors}"
        assert all(code == 200 for code in results)

    # ========== 并发会员注册 ==========

    def test_concurrent_member_registration(self, member_api, test_data):
        """测试并发会员注册"""
        results = []

        def register(i):
            response = member_api.create_member({
                "name": f"并发测试用户{i}",
                "phone": f"1380000{i:04d}",
                "gender": "male"
            })
            results.append(response.status_code)

        threads = [threading.Thread(target=register, args=(i,)) for i in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # 并发注册应该都能成功
        assert all(code == 200 for code in results)

    def test_concurrent_duplicate_registration(self, member_api):
        """测试并发重复注册（同一手机号）"""
        results = []

        def register():
            response = member_api.create_member({
                "name": "重复注册测试",
                "phone": "13800009999",
                "gender": "male"
            })
            results.append(response.json())

        threads = [threading.Thread(target=register) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # 同一手机号应该只有一次注册成功
        success_count = sum(1 for r in results if r.get("code") in [0, 200])
        assert success_count <= 1, "重复注册未被阻止"

    # ========== 并发订单状态变更 ==========

    def test_concurrent_order_status_change(self, order_api):
        """测试并发订单状态变更"""
        results = []

        def confirm_order():
            response = order_api.confirm_order("ORD_TEST_001")
            results.append(response.status_code)

        def cancel_order():
            response = order_api.cancel_order("ORD_TEST_001", "并发取消")
            results.append(response.status_code)

        # 同时确认和取消同一订单
        threads = [
            threading.Thread(target=confirm_order),
            threading.Thread(target=cancel_order)
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # 只有一个操作应该成功
        success_count = sum(1 for code in results if code == 200)
        assert success_count <= 1, "并发状态变更冲突"

    # ========== 并发查询 ==========

    def test_concurrent_query_orders(self, order_api):
        """测试并发查询订单"""
        results = []
        errors = []

        def query():
            try:
                response = order_api.get_order_list()
                results.append(response.status_code)
            except Exception as e:
                errors.append(str(e))

        threads = [threading.Thread(target=query) for _ in range(50)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0, f"并发查询出现错误: {errors}"
        assert all(code == 200 for code in results)

    def test_concurrent_query_members(self, member_api):
        """测试并发查询会员"""
        results = []
        errors = []

        def query():
            try:
                response = member_api.get_member_list()
                results.append(response.status_code)
            except Exception as e:
                errors.append(str(e))

        threads = [threading.Thread(target=query) for _ in range(50)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0, f"并发查询出现错误: {errors}"
        assert all(code == 200 for code in results)

    # ========== 并发退款 ==========

    def test_concurrent_refund(self, payment_api):
        """测试并发退款"""
        results = []

        def refund():
            response = payment_api.refund("PAY_TEST_001", 10.00, "并发退款测试")
            results.append(response.json())

        threads = [threading.Thread(target=refund) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # 同一支付单应该只有一次退款成功
        success_count = sum(1 for r in results if r.get("code") in [0, 200])
        assert success_count <= 1, "重复退款"

    # ========== 并发数据一致性 ==========

    def test_concurrent_data_consistency(self, order_api, payment_api):
        """测试并发数据一致性（下单+支付）"""
        results = []

        def order_and_pay():
            # 创建订单
            order_resp = order_api.create_order({
                "items": [{"productId": "PROD_001", "quantity": 1, "price": 10.00}],
                "payMethod": "wechat",
            })
            if order_resp.status_code == 200:
                order_id = order_resp.json()["data"]["orderId"]
                # 支付订单
                pay_resp = payment_api.create_payment({
                    "orderId": order_id,
                    "amount": 10.00,
                    "payMethod": "wechat",
                })
                results.append({
                    "order": order_resp.status_code,
                    "payment": pay_resp.status_code
                })

        threads = [threading.Thread(target=order_and_pay) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # 验证数据一致性
        assert len(results) > 0, "没有成功的订单"
        for r in results:
            assert r["order"] == 200
            assert r["payment"] == 200
