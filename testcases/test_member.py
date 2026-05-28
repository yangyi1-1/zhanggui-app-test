"""会员模块测试用例

覆盖掌柜APP会员管理功能：
- 会员列表查询
- 会员注册
- 会员详情查看
- 会员信息更新
- 会员余额查询和充值
- 会员积分查询
- 会员搜索
"""

import pytest
from utils.assertions import assert_status_code, assert_response_has_fields, assert_pagination
from utils.helpers import generate_phone


@pytest.mark.member
class TestMember:
    """会员模块测试"""

    # ========== 会员列表 ==========

    @pytest.mark.smoke
    def test_get_member_list(self, member_api):
        """测试获取会员列表"""
        response = member_api.get_member_list()
        assert_status_code(response, 200)
        data = response.json()
        assert_pagination(data)

    def test_get_member_list_with_pagination(self, member_api):
        """测试会员列表分页"""
        response = member_api.get_member_list(params={"page": 1, "pageSize": 5})
        assert_status_code(response, 200)
        data = response.json()
        assert_pagination(data)
        assert len(data["list"]) <= 5

    # ========== 会员注册 ==========

    @pytest.mark.smoke
    def test_create_member(self, member_api, test_data):
        """测试注册会员"""
        member_data = test_data["member"]["create"][0].copy()
        member_data["phone"] = generate_phone()  # 避免重复
        response = member_api.create_member(member_data)
        assert_status_code(response, 200)
        data = response.json()
        assert_response_has_fields(data["data"], ["id", "name", "phone"])

    def test_create_duplicate_phone_member(self, member_api, test_data):
        """测试重复手机号注册"""
        member_data = test_data["member"]["create"][0].copy()
        phone = generate_phone()
        member_data["phone"] = phone
        # 第一次注册
        member_api.create_member(member_data)
        # 第二次注册相同手机号
        response = member_api.create_member(member_data)
        data = response.json()
        assert data.get("code") != 0, "重复手机号应注册失败"

    # ========== 会员详情 ==========

    @pytest.mark.smoke
    def test_get_member_detail(self, member_api):
        """测试获取会员详情"""
        response = member_api.get_member_list(params={"pageSize": 1})
        data = response.json()
        if len(data["list"]) == 0:
            pytest.skip("没有可用的会员数据")
        member_id = data["list"][0]["id"]
        response = member_api.get_member_detail(member_id)
        assert_status_code(response, 200)
        detail = response.json()
        assert_response_has_fields(detail["data"], [
            "id", "name", "phone", "balance", "points", "level"
        ])

    def test_get_nonexistent_member(self, member_api):
        """测试获取不存在的会员"""
        response = member_api.get_member_detail("MEM_999")
        assert_status_code(response, 404)

    # ========== 会员信息更新 ==========

    @pytest.mark.regression
    def test_update_member(self, member_api, test_data):
        """测试更新会员信息"""
        member_data = test_data["member"]["create"][0].copy()
        member_data["phone"] = generate_phone()
        create_resp = member_api.create_member(member_data)
        assert_status_code(create_resp, 200)
        member_id = create_resp.json()["data"]["id"]

        response = member_api.update_member(member_id, {"name": "更新后的名字"})
        assert_status_code(response, 200)

    # ========== 会员余额 ==========

    def test_get_member_balance(self, member_api):
        """测试查询会员余额"""
        response = member_api.get_member_list(params={"pageSize": 1})
        data = response.json()
        if len(data["list"]) == 0:
            pytest.skip("没有可用的会员数据")
        member_id = data["list"][0]["id"]
        response = member_api.get_member_balance(member_id)
        assert_status_code(response, 200)
        balance_data = response.json()["data"]
        assert "balance" in balance_data
        assert isinstance(balance_data["balance"], (int, float))

    @pytest.mark.parametrize("amount,expected_bonus", [
        (100.00, 10.00),
        (200.00, 30.00),
        (500.00, 100.00),
    ], ids=["100_yuan", "200_yuan", "500_yuan"])
    def test_member_recharge(self, member_api, amount, expected_bonus):
        """参数化测试：会员充值（不同档位赠送）"""
        response = member_api.get_member_list(params={"pageSize": 1})
        data = response.json()
        if len(data["list"]) == 0:
            pytest.skip("没有可用的会员数据")
        member_id = data["list"][0]["id"]
        response = member_api.recharge(member_id, amount)
        assert_status_code(response, 200)
        recharge_data = response.json()["data"]
        assert recharge_data["amount"] == amount

    # ========== 会员积分 ==========

    def test_get_member_points(self, member_api):
        """测试查询会员积分"""
        response = member_api.get_member_list(params={"pageSize": 1})
        data = response.json()
        if len(data["list"]) == 0:
            pytest.skip("没有可用的会员数据")
        member_id = data["list"][0]["id"]
        response = member_api.get_member_points(member_id)
        assert_status_code(response, 200)
        points_data = response.json()["data"]
        assert "points" in points_data

    # ========== 会员搜索 ==========

    def test_search_member_by_phone(self, member_api):
        """测试按手机号搜索会员"""
        response = member_api.search_member("139")
        assert_status_code(response, 200)

    def test_search_member_by_name(self, member_api):
        """测试按姓名搜索会员"""
        response = member_api.search_member("张")
        assert_status_code(response, 200)

    def test_search_member_not_found(self, member_api):
        """测试搜索不存在的会员"""
        response = member_api.search_member("99999999999")
        assert_status_code(response, 200)
        data = response.json()
        assert len(data["data"]["list"]) == 0
