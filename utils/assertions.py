"""自定义断言模块"""


def assert_status_code(response, expected_code):
    actual = response.status_code
    assert actual == expected_code, (
        f"状态码不匹配: 期望 {expected_code}, 实际 {actual}\n"
        f"URL: {response.url}\n"
        f"Response: {response.text[:300]}"
    )


def assert_success_response(response, expected_code=200):
    assert_status_code(response, expected_code)
    data = response.json()
    assert data.get("code") == 0 or data.get("code") == 200, (
        f"业务码异常: {data.get('code')}, msg: {data.get('msg')}"
    )
    return data


def assert_response_has_fields(data, fields):
    if isinstance(data, dict):
        missing = [f for f in fields if f not in data]
        assert not missing, f"缺少字段: {missing}"
    elif isinstance(data, list) and len(data) > 0:
        missing = [f for f in fields if f not in data[0]]
        assert not missing, f"列表第一项缺少字段: {missing}"


def assert_field_value(data, field, expected_value):
    assert field in data, f"字段不存在: {field}"
    actual = data[field]
    assert actual == expected_value, (
        f"字段 {field} 值不匹配: 期望 {expected_value}, 实际 {actual}"
    )


def assert_field_not_empty(data, field):
    assert field in data, f"字段不存在: {field}"
    value = data[field]
    assert value is not None and value != "", f"字段 {field} 为空"


def assert_list_not_empty(data):
    assert isinstance(data, list), f"期望列表类型，实际: {type(data)}"
    assert len(data) > 0, "列表为空"


def assert_pagination(data, page=1, page_size=10):
    """断言分页结构"""
    assert "total" in data, "缺少total字段"
    assert "list" in data, "缺少list字段"
    assert isinstance(data["list"], list), "list字段应为列表"
