# pylint: disable=missing-function-docstring
# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=unused-argument
# pylint: disable=unused-import
# pylint: disable=too-many-arguments
# pylint: disable=redefined-builtin

import typing as tp

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from vkapi.config import VK_CONFIG


class TimeoutHTTPAdapter(HTTPAdapter):
    def __init__(self, timeout, *args, **kwargs):
        self.timeout = timeout
        if "timeout" in kwargs:
            self.timeout = kwargs["timeout"]
            del kwargs["timeout"]
        super().__init__(*args, **kwargs)

    def send(self, request, **kwargs):
        timeout = kwargs.get("timeout")
        if timeout is None:
            kwargs["timeout"] = self.timeout
        return super().send(request, **kwargs)


class Session:
    """
    Сессия.

    :param base_url: Базовый адрес, на который будут выполняться запросы.
    :param timeout: Максимальное время ожидания ответа от сервера.
    :param max_retries: Максимальное число повторных запросов.
    :param backoff_factor: Коэффициент экспоненциального нарастания задержки.
    """

    def __init__(
        self,
        base_url: str,
        timeout: float = 5.0,
        max_retries: int = 3,
        backoff_factor: float = 0.3,
    ) -> None:
        self.base_url = base_url

        new_attempt = Retry(
            total=max_retries, status_forcelist=[500, 503], backoff_factor=backoff_factor
        )
        self.session = requests.Session()

        Adapter = HTTPAdapter(max_retries=new_attempt)
        self.session.mount(self.base_url, Adapter)

    def get(self, url: str, *args: tp.Any, **kwargs: tp.Any) -> requests.Response:
        return self.send("GET", self.base_url + url, *args, **kwargs)

    def post(self, url: str, *args: tp.Any, **kwargs: tp.Any) -> requests.Response:
        return self.send("POST", self.base_url + url, *args, **kwargs)

    def send(self, method: str, url: str, *args: tp.Any, **kwargs: tp.Any) -> requests.Response:
        if "params" not in kwargs:
            kwargs["params"] = dict()
        kwargs["params"]["access_token"] = VK_CONFIG["access_token"]
        kwargs["params"]["v"] = VK_CONFIG["version"]
        request = requests.Request(method, url, *args, **kwargs)
        ready = request.prepare()
        return self.session.send(ready)
