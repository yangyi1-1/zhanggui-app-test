"""辅助工具模块"""

import time
import random
import string
from datetime import datetime


def generate_order_no():
    """生成订单号"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_str = "".join(random.choices(string.digits, k=6))
    return f"ORD{timestamp}{random_str}"


def generate_phone():
    """生成随机手机号"""
    prefixes = ["138", "139", "150", "151", "152", "186", "187", "188"]
    prefix = random.choice(prefixes)
    suffix = "".join(random.choices(string.digits, k=8))
    return f"{prefix}{suffix}"


def get_timestamp():
    """获取当前时间戳（毫秒）"""
    return int(time.time() * 1000)


def get_current_date():
    """获取当前日期 YYYY-MM-DD"""
    return datetime.now().strftime("%Y-%m-%d")


def get_current_datetime():
    """获取当前日期时间 YYYY-MM-DD HH:MM:SS"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
