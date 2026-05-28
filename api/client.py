"""API客户端基类

封装通用的HTTP请求方法，所有API模块继承此类。
"""

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from config.config import BASE_URL, TIMEOUT, HEADERS
from utils.logger import logger


class APIClient:
    """API客户端基类"""

    def __init__(self, base_url=None):
        self.base_url = base_url or BASE_URL
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.token = None

        # 配置重试策略
        retry = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[500, 502, 503, 504],
        )
        self.session.mount("http://", HTTPAdapter(max_retries=retry))
        self.session.mount("https://", HTTPAdapter(max_retries=retry))

    def set_token(self, token):
        """设置认证Token"""
        self.token = token
        self.session.headers["Authorization"] = f"Bearer {token}"

    def clear_token(self):
        """清除认证Token"""
        self.token = None
        self.session.headers.pop("Authorization", None)

    def _request(self, method, path, **kwargs):
        url = f"{self.base_url}{path}"
        kwargs.setdefault("timeout", TIMEOUT)

        logger.info(f"[{method}] {url}")
        if "json" in kwargs:
            logger.info(f"Request Body: {kwargs['json']}")
        if "params" in kwargs:
            logger.info(f"Params: {kwargs['params']}")

        response = self.session.request(method, url, **kwargs)

        logger.info(f"Status: {response.status_code}")
        logger.info(f"Response: {response.text[:500]}")

        # 检查 Token 过期
        if response.status_code == 401:
            logger.warning("Token 已过期，请重新登录获取新 Token")

        return response

    def get(self, path, **kwargs):
        return self._request("GET", path, **kwargs)

    def post(self, path, **kwargs):
        return self._request("POST", path, **kwargs)

    def put(self, path, **kwargs):
        return self._request("PUT", path, **kwargs)

    def delete(self, path, **kwargs):
        return self._request("DELETE", path, **kwargs)
