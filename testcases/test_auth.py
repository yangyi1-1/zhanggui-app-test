"""认证模块测试用例

覆盖掌柜APP登录认证功能：
- 正常登录
- 异常登录（密码错误、用户不存在、参数缺失）
- Token刷新
- 用户信息获取
- 登出
"""

import pytest
from api.auth_api import AuthAPI
from utils.assertions import assert_status_code, assert_response_has_fields


@pytest.mark.auth
class TestAuth:
    """认证模块测试"""

    def setup_method(self):
        self.api = AuthAPI()

    # ========== 登录测试 ==========

    @pytest.mark.smoke
    def test_login_success(self, test_data):
        """测试正常登录"""
        account = test_data["auth"]["valid_login"]
        response = self.api.login(account["phone"], account["password"])
        assert_status_code(response, 200)
        data = response.json()
        assert data.get("code") in [0, 200], f"登录失败: {data.get('msg')}"
        assert_response_has_fields(data["data"], ["token", "userInfo"])

    @pytest.mark.parametrize("phone,password,expected_msg", [
        ("13800000001", "wrong_password", "密码错误"),
        ("19900000000", "test123456", "用户不存在"),
        ("", "test123456", "手机号不能为空"),
        ("13800000001", "", "密码不能为空"),
    ], ids=["wrong_password", "nonexistent_user", "empty_phone", "empty_password"])
    def test_login_failure(self, phone, password, expected_msg):
        """参数化测试：异常登录场景"""
        response = self.api.login(phone, password)
        assert_status_code(response, 200)
        data = response.json()
        assert data.get("code") != 0, f"预期登录失败，但成功了"
        assert expected_msg in data.get("msg", ""), (
            f"错误信息不匹配: 预期包含 '{expected_msg}', 实际 '{data.get('msg')}'"
        )

    def test_login_phone_format_invalid(self):
        """测试手机号格式错误"""
        response = self.api.login("abc123", "test123456")
        assert_status_code(response, 200)
        data = response.json()
        assert data.get("code") != 0

    # ========== 用户信息测试 ==========

    @pytest.mark.smoke
    def test_get_user_info(self, admin_token):
        """测试获取用户信息"""
        self.api.set_token(admin_token)
        response = self.api.get_user_info()
        assert_status_code(response, 200)
        data = response.json()
        assert_response_has_fields(data["data"], ["id", "name", "phone", "role"])

    def test_get_user_info_without_token(self):
        """测试未登录获取用户信息"""
        response = self.api.get_user_info()
        assert_status_code(response, 401)

    # ========== Token测试 ==========

    def test_refresh_token(self, admin_token):
        """测试刷新Token"""
        self.api.set_token(admin_token)
        response = self.api.refresh_token()
        assert_status_code(response, 200)
        data = response.json()
        assert_response_has_fields(data["data"], ["token"])

    # ========== 登出测试 ==========

    @pytest.mark.regression
    def test_logout(self, admin_token):
        """测试登出"""
        self.api.set_token(admin_token)
        response = self.api.logout()
        assert_status_code(response, 200)

    def test_operations_after_logout(self):
        """测试登出后访问需认证接口"""
        response = self.api.get_user_info()
        assert_status_code(response, 401)
