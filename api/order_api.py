"""订单模块API"""

from api.client import APIClient


class OrderAPI(APIClient):
    """订单相关接口"""

    def get_order_list(self, params=None):
        """获取订单列表"""
        return self.get("/api/v1/orders", params=params)

    def get_order_detail(self, order_id):
        """获取订单详情"""
        return self.get(f"/api/v1/orders/{order_id}")

    def create_order(self, data):
        """创建订单"""
        return self.post("/api/v1/orders", json=data)

    def cancel_order(self, order_id, reason=None):
        """取消订单"""
        return self.post(f"/api/v1/orders/{order_id}/cancel", json={
            "reason": reason or "用户取消"
        })

    def confirm_order(self, order_id):
        """确认订单"""
        return self.post(f"/api/v1/orders/{order_id}/confirm")

    def complete_order(self, order_id):
        """完成订单"""
        return self.post(f"/api/v1/orders/{order_id}/complete")

    def refund_order(self, order_id, data):
        """退款"""
        return self.post(f"/api/v1/orders/{order_id}/refund", json=data)

    def get_order_items(self, order_id):
        """获取订单商品明细"""
        return self.get(f"/api/v1/orders/{order_id}/items")

    def search_orders(self, keyword):
        """搜索订单"""
        return self.get("/api/v1/orders/search", params={"keyword": keyword})
