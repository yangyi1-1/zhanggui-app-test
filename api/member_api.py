"""会员模块API"""

from api.client import APIClient


class MemberAPI(APIClient):
    """会员相关接口"""

    def get_member_list(self, params=None):
        """获取会员列表"""
        return self.get("/api/v1/members", params=params)

    def get_member_detail(self, member_id):
        """获取会员详情"""
        return self.get(f"/api/v1/members/{member_id}")

    def create_member(self, data):
        """注册会员"""
        return self.post("/api/v1/members", json=data)

    def update_member(self, member_id, data):
        """更新会员信息"""
        return self.put(f"/api/v1/members/{member_id}", json=data)

    def get_member_balance(self, member_id):
        """查询会员余额"""
        return self.get(f"/api/v1/members/{member_id}/balance")

    def recharge(self, member_id, amount):
        """会员充值"""
        return self.post(f"/api/v1/members/{member_id}/recharge", json={
            "amount": amount
        })

    def get_member_points(self, member_id):
        """查询会员积分"""
        return self.get(f"/api/v1/members/{member_id}/points")

    def search_member(self, keyword):
        """搜索会员（手机号/姓名）"""
        return self.get("/api/v1/members/search", params={"keyword": keyword})

    def exchange_points(self, member_id, points, item_id):
        """积分兑换"""
        return self.post(f"/api/v1/members/{member_id}/exchange", json={
            "points": points,
            "itemId": item_id
        })

    def get_member_level(self, member_id):
        """获取会员等级"""
        return self.get(f"/api/v1/members/{member_id}/level")

    def update_member_level(self, member_id, level):
        """更新会员等级"""
        return self.put(f"/api/v1/members/{member_id}/level", json={"level": level})

    def get_member_consume_records(self, member_id, params=None):
        """获取会员消费记录"""
        return self.get(f"/api/v1/members/{member_id}/consume", params=params)

    def get_member_tags(self, member_id):
        """获取会员标签"""
        return self.get(f"/api/v1/members/{member_id}/tags")

    def add_member_tag(self, member_id, tag):
        """添加会员标签"""
        return self.post(f"/api/v1/members/{member_id}/tags", json={"tag": tag})

    def report_loss(self, member_id, reason=None):
        """会员卡挂失"""
        return self.post(f"/api/v1/members/{member_id}/loss", json={
            "reason": reason or "遗失"
        })

    def unblock(self, member_id):
        """会员卡解挂"""
        return self.post(f"/api/v1/members/{member_id}/unblock")

    def get_member_statistics(self, params=None):
        """获取会员统计"""
        return self.get("/api/v1/members/statistics", params=params)
