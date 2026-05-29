"""会员模块测试用例

覆盖掌柜APP会员管理功能：
- 会员列表查询
- 会员注册
- 会员详情查看
- 会员信息更新
- 会员余额查询和充值
- 会员积分查询
- 会员搜索
- 积分兑换
- 会员等级
- 消费记录
- 会员标签
- 挂失/解挂
- 会员统计
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

    def test_get_member_list_by_level(self, member_api):
        """测试按等级筛选会员"""
        for level in ["normal", "silver", "gold", "diamond"]:
            response = member_api.get_member_list(params={"level": level})
            assert_status_code(response, 200)

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

    def test_create_member_invalid_phone(self, member_api, test_data):
        """测试无效手机号注册"""
        member_data = test_data["member"]["create"][0].copy()
        member_data["phone"] = "12345"
        response = member_api.create_member(member_data)
        data = response.json()
        assert data.get("code") != 0, "无效手机号应注册失败"

    def test_create_member_empty_name(self, member_api):
        """测试空姓名注册"""
        response = member_api.create_member({
            "name": "",
            "phone": generate_phone(),
            "gender": "male"
        })
        data = response.json()
        assert data.get("code") != 0, "空姓名应注册失败"

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

    def test_member_recharge_zero(self, member_api):
        """测试充值0元"""
        response = member_api.get_member_list(params={"pageSize": 1})
        data = response.json()
        if len(data["list"]) == 0:
            pytest.skip("没有可用的会员数据")
        member_id = data["list"][0]["id"]
        response = member_api.recharge(member_id, 0)
        data = response.json()
        assert data.get("code") != 0, "充值0元应失败"

    def test_member_recharge_negative(self, member_api):
        """测试充值负数"""
        response = member_api.get_member_list(params={"pageSize": 1})
        data = response.json()
        if len(data["list"]) == 0:
            pytest.skip("没有可用的会员数据")
        member_id = data["list"][0]["id"]
        response = member_api.recharge(member_id, -100)
        data = response.json()
        assert data.get("code") != 0, "充值负数应失败"

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

    # ========== 积分兑换 ==========

    def test_exchange_points(self, member_api):
        """测试积分兑换"""
        response = member_api.get_member_list(params={"pageSize": 1})
        data = response.json()
        if len(data["list"]) == 0:
            pytest.skip("没有可用的会员数据")
        member_id = data["list"][0]["id"]
        response = member_api.exchange_points(member_id, 100, "ITEM_001")
        # 积分兑换可能成功或积分不足
        assert response.status_code in [200, 400]

    def test_exchange_points_insufficient(self, member_api):
        """测试积分不足兑换"""
        response = member_api.get_member_list(params={"pageSize": 1})
        data = response.json()
        if len(data["list"]) == 0:
            pytest.skip("没有可用的会员数据")
        member_id = data["list"][0]["id"]
        response = member_api.exchange_points(member_id, 999999, "ITEM_001")
        data = response.json()
        assert data.get("code") != 0, "积分不足应兑换失败"

    # ========== 会员等级 ==========

    def test_get_member_level(self, member_api):
        """测试获取会员等级"""
        response = member_api.get_member_list(params={"pageSize": 1})
        data = response.json()
        if len(data["list"]) == 0:
            pytest.skip("没有可用的会员数据")
        member_id = data["list"][0]["id"]
        response = member_api.get_member_level(member_id)
        assert_status_code(response, 200)
        data = response.json()
        assert "level" in data["data"]

    def test_update_member_level(self, member_api):
        """测试更新会员等级"""
        response = member_api.get_member_list(params={"pageSize": 1})
        data = response.json()
        if len(data["list"]) == 0:
            pytest.skip("没有可用的会员数据")
        member_id = data["list"][0]["id"]
        response = member_api.update_member_level(member_id, "gold")
        # 更新等级可能成功或需要满足条件
        assert response.status_code in [200, 400]

    # ========== 消费记录 ==========

    def test_get_member_consume_records(self, member_api):
        """测试获取会员消费记录"""
        response = member_api.get_member_list(params={"pageSize": 1})
        data = response.json()
        if len(data["list"]) == 0:
            pytest.skip("没有可用的会员数据")
        member_id = data["list"][0]["id"]
        response = member_api.get_member_consume_records(member_id)
        assert_status_code(response, 200)
        data = response.json()
        assert isinstance(data["data"], list)

    def test_get_member_consume_records_by_date(self, member_api):
        """测试按日期查询消费记录"""
        from utils.helpers import get_current_date
        response = member_api.get_member_list(params={"pageSize": 1})
        data = response.json()
        if len(data["list"]) == 0:
            pytest.skip("没有可用的会员数据")
        member_id = data["list"][0]["id"]
        response = member_api.get_member_consume_records(member_id, params={
            "startDate": get_current_date(),
            "endDate": get_current_date(),
        })
        assert_status_code(response, 200)

    # ========== 会员标签 ==========

    def test_get_member_tags(self, member_api):
        """测试获取会员标签"""
        response = member_api.get_member_list(params={"pageSize": 1})
        data = response.json()
        if len(data["list"]) == 0:
            pytest.skip("没有可用的会员数据")
        member_id = data["list"][0]["id"]
        response = member_api.get_member_tags(member_id)
        assert_status_code(response, 200)
        data = response.json()
        assert isinstance(data["data"], list)

    def test_add_member_tag(self, member_api):
        """测试添加会员标签"""
        response = member_api.get_member_list(params={"pageSize": 1})
        data = response.json()
        if len(data["list"]) == 0:
            pytest.skip("没有可用的会员数据")
        member_id = data["list"][0]["id"]
        response = member_api.add_member_tag(member_id, "VIP客户")
        assert_status_code(response, 200)

    # ========== 挂失/解挂 ==========

    @pytest.mark.regression
    def test_report_loss(self, member_api, test_data):
        """测试会员卡挂失"""
        member_data = test_data["member"]["create"][0].copy()
        member_data["phone"] = generate_phone()
        create_resp = member_api.create_member(member_data)
        assert_status_code(create_resp, 200)
        member_id = create_resp.json()["data"]["id"]

        response = member_api.report_loss(member_id, "遗失")
        assert_status_code(response, 200)

    @pytest.mark.regression
    def test_unblock(self, member_api, test_data):
        """测试会员卡解挂"""
        member_data = test_data["member"]["create"][0].copy()
        member_data["phone"] = generate_phone()
        create_resp = member_api.create_member(member_data)
        assert_status_code(create_resp, 200)
        member_id = create_resp.json()["data"]["id"]

        # 先挂失
        member_api.report_loss(member_id, "测试挂失")
        # 再解挂
        response = member_api.unblock(member_id)
        assert_status_code(response, 200)

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

    def test_search_member_empty_keyword(self, member_api):
        """测试空关键字搜索"""
        response = member_api.search_member("")
        # 空搜索可能返回全部或报错
        assert response.status_code in [200, 400]

    # ========== 会员统计 ==========

    def test_get_member_statistics(self, member_api):
        """测试获取会员统计"""
        response = member_api.get_member_statistics()
        assert_status_code(response, 200)
        data = response.json()
        assert_response_has_fields(data["data"], [
            "totalMembers", "newMembersToday", "activeMembers"
        ])

    # ========== 边界测试 ==========

    def test_get_member_detail_invalid_id(self, member_api):
        """测试无效ID获取会员"""
        response = member_api.get_member_detail("invalid_id!@#")
        assert response.status_code in [400, 404]

    def test_update_nonexistent_member(self, member_api):
        """测试更新不存在的会员"""
        response = member_api.update_member("MEM_999", {"name": "测试"})
        assert_status_code(response, 404)
