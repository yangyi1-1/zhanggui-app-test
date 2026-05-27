"""API客户端基类

封装通用的HTTP请求方法，所有API模块继承此类。
"""

import requests
from config.config import BASE_URL, TIMEOUT, HEADERS
from utils.logger import logger


class APIClient:
    """API客户端基类"""

    def __init__(self, base_url=None):
        self.base_url = base_url or BASE_URL
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.token = None

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

        return response

    def get(self, path, **kwargs):
        return self._request("GET", path, **kwargs)

    def post(self, path, **kwargs):
        return self._request("POST", path, **kwargs)

    def put(self, path, **kwargs):
        return self._request("PUT", path, **kwargs)

    def delete(self, path, **kwargs):
        return self._request("DELETE", path, **kwargs)
