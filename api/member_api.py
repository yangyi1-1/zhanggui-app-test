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
