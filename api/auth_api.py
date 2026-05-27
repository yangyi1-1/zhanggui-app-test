"""认证模块API"""

from api.client import APIClient


class AuthAPI(APIClient):
    """认证相关接口"""

    def login(self, phone, password):
        """登录"""
        return self.post("/api/v1/auth/login", json={
            "phone": phone,
            "password": password,
        })

    def logout(self):
        """登出"""
        return self.post("/api/v1/auth/logout")

    def refresh_token(self):
        """刷新Token"""
        return self.post("/api/v1/auth/refresh")

    def get_user_info(self):
        """获取当前用户信息"""
        return self.get("/api/v1/auth/userinfo")

    def change_password(self, old_password, new_password):
        """修改密码"""
        return self.post("/api/v1/auth/change-password", json={
            "oldPassword": old_password,
            "newPassword": new_password,
        })
