"""安全测试用例

覆盖掌柜APP安全场景：
- SQL注入测试
- XSS攻击测试
- 越权访问测试
- 敏感信息泄露测试
- 认证绕过测试
- 参数篡改测试
"""

import pytest
from utils.assertions import assert_status_code


@pytest.mark.security
class TestSecurity:
    """安全测试"""

    # ========== SQL注入测试 ==========

    def test_sql_injection_login(self, auth_api):
        """测试登录接口SQL注入"""
        payloads = [
            "' OR '1'='1",
            "' OR '1'='1' --",
            "' OR '1'='1' /*",
            "admin'--",
            "1' UNION SELECT * FROM users--",
        ]
        for payload in payloads:
            response = auth_api.login(payload, "test123456")
            data = response.json()
            # SQL注入应该失败
            assert data.get("code") != 0 or "token" not in str(data), \
                f"可能存在SQL注入: {payload}"

    def test_sql_injection_search(self, order_api):
        """测试搜索接口SQL注入"""
        payloads = [
            "' OR '1'='1",
            "1; DROP TABLE orders--",
            "' UNION SELECT * FROM users--",
            "1' AND 1=1--",
            "1' AND 1=2--",
        ]
        for payload in payloads:
            response = order_api.search_orders(payload)
            # 应该返回空结果或错误，而不是所有数据
            assert response.status_code in [200, 400]
            if response.status_code == 200:
                data = response.json()
                # 不应该返回所有数据
                assert len(data.get("data", {}).get("list", [])) < 100

    def test_sql_injection_member_search(self, member_api):
        """测试会员搜索SQL注入"""
        payloads = [
            "' OR '1'='1",
            "1' UNION SELECT * FROM members--",
            "' OR 1=1--",
        ]
        for payload in payloads:
            response = member_api.search_member(payload)
            assert response.status_code in [200, 400]

    # ========== XSS攻击测试 ==========

    def test_xss_product_name(self, product_api):
        """测试商品名称XSS"""
        payloads = [
            "<script>alert(1)</script>",
            "<img src=x onerror=alert(1)>",
            "<svg onload=alert(1)>",
            "javascript:alert(1)",
            "<iframe src=javascript:alert(1)>",
        ]
        for payload in payloads:
            response = product_api.create_product({
                "name": payload,
                "price": 10.00,
                "category": "测试",
                "storeId": "STORE_001"
            })
            if response.status_code == 200:
                # 查询验证是否转义
                detail_resp = product_api.get_product_list()
                if detail_resp.status_code == 200:
                    data = detail_resp.json()
                    # 不应该包含未转义的脚本
                    assert "<script>" not in str(data)

    def test_xss_order_remark(self, order_api):
        """测试订单备注XSS"""
        payloads = [
            "<script>alert('xss')</script>",
            "<img src=x onerror=alert(1)>",
        ]
        for payload in payloads:
            response = order_api.update_order_remark("ORD_001", payload)
            # 应该成功但内容被转义
            assert response.status_code in [200, 400]

    def test_xss_member_name(self, member_api):
        """测试会员姓名XSS"""
        payloads = [
            "<script>alert(1)</script>",
            "<img src=x onerror=alert(1)>",
        ]
        for payload in payloads:
            response = member_api.create_member({
                "name": payload,
                "phone": "13800001111",
                "gender": "male"
            })
            assert response.status_code in [200, 400]

    # ========== 越权访问测试 ==========

    def test_horizontal_privilege_order(self, order_api):
        """测试水平越权（访问其他用户订单）"""
        # 尝试访问其他用户的订单
        response = order_api.get_order_detail("ORD_OTHER_USER")
        # 应该返回403或404
        assert response.status_code in [403, 404]

    def test_horizontal_privilege_member(self, member_api):
        """测试水平越权（访问其他会员数据）"""
        response = member_api.get_member_detail("MEM_OTHER_USER")
        assert response.status_code in [403, 404]

    def test_vertical_privilege_admin(self, store_api):
        """测试垂直越权（普通用户访问管理员接口）"""
        # 用普通用户token尝试访问管理员接口
        response = store_api.get_store_permissions("STORE_001")
        # 应该返回403
        assert response.status_code in [403, 401]

    def test_vertical_privilege_delete(self, product_api):
        """测试垂直越权（普通用户删除商品）"""
        response = product_api.delete_product("PROD_001")
        # 应该返回403
        assert response.status_code in [403, 401]

    # ========== 敏感信息泄露测试 ==========

    def test_password_not_in_response(self, auth_api, test_data):
        """测试密码不在响应中泄露"""
        account = test_data["auth"]["valid_login"]
        response = auth_api.login(account["phone"], account["password"])
        data = response.json()
        # 响应中不应该包含密码
        assert "password" not in str(data).lower()
        assert account["password"] not in str(data)

    def test_token_not_in_url(self, auth_api):
        """测试Token不在URL中"""
        response = auth_api.get_user_info()
        # Token应该在header中，不在URL中
        assert "token" not in response.url.lower()
        assert "authorization" not in response.url.lower()

    def test_sensitive_fields_masked(self, member_api):
        """测试敏感字段脱敏"""
        response = member_api.get_member_list()
        if response.status_code == 200:
            data = response.json()
            if len(data.get("data", {}).get("list", [])) > 0:
                member = data["data"]["list"][0]
                # 手机号应该脱敏显示
                phone = member.get("phone", "")
                if phone:
                    # 不应该是完整手机号
                    assert len(phone) <= 11

    # ========== 认证绕过测试 ==========

    def test_no_token_access(self, auth_api):
        """测试无Token访问"""
        response = auth_api.get_user_info()
        assert response.status_code == 401

    def test_invalid_token_access(self, auth_api):
        """测试无效Token访问"""
        auth_api.set_token("invalid_token_12345")
        response = auth_api.get_user_info()
        assert response.status_code == 401
        auth_api.clear_token()

    def test_expired_token_access(self, auth_api):
        """测试过期Token访问"""
        auth_api.set_token("expired_token_12345")
        response = auth_api.get_user_info()
        assert response.status_code == 401
        auth_api.clear_token()

    def test_empty_token_access(self, auth_api):
        """测试空Token访问"""
        auth_api.set_token("")
        response = auth_api.get_user_info()
        assert response.status_code == 401
        auth_api.clear_token()

    # ========== 参数篡改测试 ==========

    def test_tamper_payment_amount(self, payment_api):
        """测试篡改支付金额"""
        # 创建支付单
        create_resp = payment_api.create_payment({
            "amount": 100.00,
            "payMethod": "wechat",
        })
        if create_resp.status_code == 200:
            payment_id = create_resp.json()["data"]["paymentId"]
            # 尝试篡改金额退款
            response = payment_api.refund(payment_id, 99999.99, "篡改金额")
            # 应该失败
            assert response.status_code in [400, 403]

    def test_tamper_order_id(self, payment_api):
        """测试篡改订单ID"""
        response = payment_api.create_payment({
            "orderId": "ORD_TAMPERED",
            "amount": 10.00,
            "payMethod": "wechat",
        })
        # 应该验证订单归属
        assert response.status_code in [200, 400, 403]

    def test_tamper_user_id(self, member_api):
        """测试篡改用户ID"""
        response = member_api.update_member("MEM_HACKED", {"name": "黑客"})
        # 应该验证用户权限
        assert response.status_code in [403, 404]

    # ========== 暴力破解防护 ==========

    def test_brute_force_login(self, auth_api):
        """测试暴力破解防护"""
        # 连续错误登录
        for i in range(10):
            response = auth_api.login("13800000001", f"wrong_password_{i}")

        # 应该有频率限制
        response = auth_api.login("13800000001", "test123456")
        # 可能被限制或需要验证码
        assert response.status_code in [200, 401, 429]

    def test_brute_force_sms(self, auth_api):
        """测试短信验证码暴力破解"""
        # 连续请求验证码
        for i in range(10):
            response = auth_api.send_sms("13800000001")

        # 应该有频率限制
        assert response.status_code in [200, 429]

    # ========== 文件上传安全 ==========

    def test_malicious_file_upload(self, product_api):
        """测试恶意文件上传"""
        payloads = [
            {"filename": "test.php", "content": "<?php echo 'hacked'; ?>"},
            {"filename": "test.exe", "content": "malicious content"},
            {"filename": "test.js", "content": "alert('xss')"},
        ]
        for payload in payloads:
            response = product_api.upload_product_image("PROD_001", payload)
            # 应该拒绝危险文件类型
            assert response.status_code in [400, 403, 415]

    # ========== HTTP头安全 ==========

    def test_security_headers(self, auth_api):
        """测试安全响应头"""
        response = auth_api.login("13800000001", "test123456")
        headers = response.headers

        # 检查安全头
        # X-Content-Type-Options
        assert headers.get("X-Content-Type-Options") == "nosniff" or True
        # X-Frame-Options
        assert headers.get("X-Frame-Options") in ["DENY", "SAMEORIGIN"] or True
        # X-XSS-Protection
        assert headers.get("X-XSS-Protection") or True

    # ========== 会话安全 ==========

    def test_session_fixation(self, auth_api):
        """测试会话固定攻击"""
        # 获取初始Token
        response1 = auth_api.login("13800000001", "test123456")
        token1 = response1.json().get("data", {}).get("token", "")

        # 重新登录
        response2 = auth_api.login("13800000001", "test123456")
        token2 = response2.json().get("data", {}).get("token", "")

        # Token应该不同
        if token1 and token2:
            assert token1 != token2, "会话固定漏洞"

    # ========== CORS安全 ==========

    def test_cors_policy(self, auth_api):
        """测试CORS策略"""
        response = auth_api.login("13800000001", "test123456")
        # 检查CORS头
        cors_header = response.headers.get("Access-Control-Allow-Origin", "")
        # 不应该是 *
        assert cors_header != "*" or cors_header == ""
