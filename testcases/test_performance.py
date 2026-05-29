"""性能测试用例

覆盖掌柜APP性能场景：
- 接口响应时间测试
- 并发性能测试
- 大数据量测试
- 超时测试
"""

import pytest
import time
from utils.assertions import assert_status_code


@pytest.mark.performance
class TestPerformance:
    """性能测试"""

    # ========== 响应时间测试 ==========

    def test_login_response_time(self, auth_api, test_data):
        """测试登录接口响应时间"""
        account = test_data["auth"]["valid_login"]
        start = time.time()
        response = auth_api.login(account["phone"], account["password"])
        elapsed = time.time() - start

        assert_status_code(response, 200)
        assert elapsed < 2.0, f"登录接口响应时间过长: {elapsed:.2f}s"

    def test_order_list_response_time(self, order_api):
        """测试订单列表响应时间"""
        start = time.time()
        response = order_api.get_order_list()
        elapsed = time.time() - start

        assert_status_code(response, 200)
        assert elapsed < 3.0, f"订单列表响应时间过长: {elapsed:.2f}s"

    def test_product_list_response_time(self, product_api):
        """测试商品列表响应时间"""
        start = time.time()
        response = product_api.get_product_list()
        elapsed = time.time() - start

        assert_status_code(response, 200)
        assert elapsed < 2.0, f"商品列表响应时间过长: {elapsed:.2f}s"

    def test_member_list_response_time(self, member_api):
        """测试会员列表响应时间"""
        start = time.time()
        response = member_api.get_member_list()
        elapsed = time.time() - start

        assert_status_code(response, 200)
        assert elapsed < 2.0, f"会员列表响应时间过长: {elapsed:.2f}s"

    def test_payment_create_response_time(self, payment_api):
        """测试创建支付响应时间"""
        start = time.time()
        response = payment_api.create_payment({
            "amount": 10.00,
            "payMethod": "wechat",
        })
        elapsed = time.time() - start

        assert_status_code(response, 200)
        assert elapsed < 3.0, f"创建支付响应时间过长: {elapsed:.2f}s"

    def test_order_detail_response_time(self, order_api):
        """测试订单详情响应时间"""
        # 先获取一个订单ID
        list_resp = order_api.get_order_list(params={"pageSize": 1})
        if list_resp.status_code == 200:
            data = list_resp.json()
            if len(data.get("list", [])) > 0:
                order_id = data["list"][0]["id"]
                start = time.time()
                response = order_api.get_order_detail(order_id)
                elapsed = time.time() - start

                assert_status_code(response, 200)
                assert elapsed < 1.0, f"订单详情响应时间过长: {elapsed:.2f}s"

    # ========== 分页性能测试 ==========

    def test_pagination_performance_page1(self, order_api):
        """测试分页性能（第1页）"""
        start = time.time()
        response = order_api.get_order_list(params={"page": 1, "pageSize": 20})
        elapsed = time.time() - start

        assert_status_code(response, 200)
        assert elapsed < 2.0, f"分页查询响应时间过长: {elapsed:.2f}s"

    def test_pagination_performance_page10(self, order_api):
        """测试分页性能（第10页）"""
        start = time.time()
        response = order_api.get_order_list(params={"page": 10, "pageSize": 20})
        elapsed = time.time() - start

        assert_status_code(response, 200)
        assert elapsed < 3.0, f"深分页查询响应时间过长: {elapsed:.2f}s"

    def test_pagination_performance_large_page(self, order_api):
        """测试大页面分页性能"""
        start = time.time()
        response = order_api.get_order_list(params={"page": 1, "pageSize": 100})
        elapsed = time.time() - start

        assert_status_code(response, 200)
        assert elapsed < 5.0, f"大页面查询响应时间过长: {elapsed:.2f}s"

    # ========== 搜索性能测试 ==========

    def test_search_performance(self, order_api):
        """测试搜索性能"""
        start = time.time()
        response = order_api.search_orders("ORD")
        elapsed = time.time() - start

        assert_status_code(response, 200)
        assert elapsed < 3.0, f"搜索响应时间过长: {elapsed:.2f}s"

    def test_member_search_performance(self, member_api):
        """测试会员搜索性能"""
        start = time.time()
        response = member_api.search_member("138")
        elapsed = time.time() - start

        assert_status_code(response, 200)
        assert elapsed < 2.0, f"会员搜索响应时间过长: {elapsed:.2f}s"

    # ========== 统计接口性能 ==========

    def test_order_statistics_performance(self, order_api):
        """测试订单统计性能"""
        start = time.time()
        response = order_api.get_order_statistics()
        elapsed = time.time() - start

        assert_status_code(response, 200)
        assert elapsed < 5.0, f"订单统计响应时间过长: {elapsed:.2f}s"

    def test_payment_statistics_performance(self, payment_api):
        """测试支付统计性能"""
        start = time.time()
        response = payment_api.get_payment_statistics()
        elapsed = time.time() - start

        assert_status_code(response, 200)
        assert elapsed < 5.0, f"支付统计响应时间过长: {elapsed:.2f}s"

    def test_member_statistics_performance(self, member_api):
        """测试会员统计性能"""
        start = time.time()
        response = member_api.get_member_statistics()
        elapsed = time.time() - start

        assert_status_code(response, 200)
        assert elapsed < 5.0, f"会员统计响应时间过长: {elapsed:.2f}s"

    # ========== 批量操作性能 ==========

    def test_batch_create_performance(self, order_api):
        """测试批量创建性能"""
        start = time.time()
        for i in range(10):
            order_api.create_order({
                "items": [{"productId": f"PROD_{i:03d}", "quantity": 1, "price": 10.00}],
                "payMethod": "wechat",
            })
        elapsed = time.time() - start

        assert elapsed < 30.0, f"批量创建耗时过长: {elapsed:.2f}s"

    # ========== 超时测试 ==========

    def test_request_timeout(self, order_api):
        """测试请求超时"""
        # 设置很短的超时时间
        try:
            response = order_api.get_order_list(timeout=0.001)
            # 如果成功，说明响应很快
            assert response.status_code == 200
        except Exception as e:
            # 应该抛出超时异常
            assert "timeout" in str(e).lower() or "timed out" in str(e).lower()

    # ========== 大数据量测试 ==========

    def test_large_order_list(self, order_api):
        """测试大数据量订单列表"""
        start = time.time()
        response = order_api.get_order_list(params={"pageSize": 1000})
        elapsed = time.time() - start

        assert_status_code(response, 200)
        assert elapsed < 10.0, f"大数据量查询响应时间过长: {elapsed:.2f}s"

    def test_large_member_list(self, member_api):
        """测试大数据量会员列表"""
        start = time.time()
        response = member_api.get_member_list(params={"pageSize": 1000})
        elapsed = time.time() - start

        assert_status_code(response, 200)
        assert elapsed < 10.0, f"大数据量查询响应时间过长: {elapsed:.2f}s"

    # ========== 导出性能测试 ==========

    def test_export_orders_performance(self, order_api):
        """测试订单导出性能"""
        start = time.time()
        response = order_api.export_orders()
        elapsed = time.time() - start

        assert_status_code(response, 200)
        assert elapsed < 30.0, f"订单导出响应时间过长: {elapsed:.2f}s"

    def test_export_store_data_performance(self, store_api):
        """测试门店数据导出性能"""
        start = time.time()
        response = store_api.export_store_data("STORE_001")
        elapsed = time.time() - start

        assert_status_code(response, 200)
        assert elapsed < 30.0, f"门店数据导出响应时间过长: {elapsed:.2f}s"

    # ========== 连续请求性能 ==========

    def test_sequential_requests_performance(self, order_api):
        """测试连续请求性能"""
        start = time.time()
        for _ in range(100):
            response = order_api.get_order_list()
            assert_status_code(response, 200)
        elapsed = time.time() - start

        avg_time = elapsed / 100
        assert avg_time < 0.5, f"平均响应时间过长: {avg_time:.2f}s"

    # ========== 性能基准测试 ==========

    def test_performance_baseline(self, auth_api, test_data):
        """测试性能基准（多次测量取平均）"""
        account = test_data["auth"]["valid_login"]
        times = []

        for _ in range(10):
            start = time.time()
            response = auth_api.login(account["phone"], account["password"])
            elapsed = time.time() - start
            times.append(elapsed)
            assert_status_code(response, 200)

        avg_time = sum(times) / len(times)
        max_time = max(times)
        min_time = min(times)

        # 记录性能数据
        print(f"\n登录接口性能基准:")
        print(f"  平均响应时间: {avg_time:.3f}s")
        print(f"  最大响应时间: {max_time:.3f}s")
        print(f"  最小响应时间: {min_time:.3f}s")

        assert avg_time < 1.0, f"平均响应时间过长: {avg_time:.3f}s"
        assert max_time < 3.0, f"最大响应时间过长: {max_time:.3f}s"
