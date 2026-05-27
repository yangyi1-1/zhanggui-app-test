"""支付模块API"""

from api.client import APIClient


class PaymentAPI(APIClient):
    """支付相关接口"""

    def create_payment(self, data):
        """创建支付单"""
        return self.post("/api/v1/payments", json=data)

    def get_payment_status(self, payment_id):
        """查询支付状态"""
        return self.get(f"/api/v1/payments/{payment_id}/status")

    def payment_callback(self, data):
        """支付回调（模拟）"""
        return self.post("/api/v1/payments/callback", json=data)

    def get_payment_list(self, params=None):
        """获取支付记录列表"""
        return self.get("/api/v1/payments", params=params)

    def refund(self, payment_id, amount, reason):
        """退款"""
        return self.post(f"/api/v1/payments/{payment_id}/refund", json={
            "amount": amount,
            "reason": reason,
        })

    def get_refund_status(self, refund_id):
        """查询退款状态"""
        return self.get(f"/api/v1/payments/refund/{refund_id}")

    def get_daily_settlement(self, store_id, date):
        """获取日结算数据"""
        return self.get("/api/v1/payments/settlement", params={
            "storeId": store_id,
            "date": date,
        })
