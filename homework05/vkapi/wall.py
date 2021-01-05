# pylint: disable=missing-function-docstring
# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=unused-argument
# pylint: disable=unused-import
# pylint: disable=too-many-arguments
# pylint: disable=redefined-builtin

import math
import textwrap
import time
import typing as tp
from string import Template

import pandas as pd
from pandas import json_normalize

from vkapi import session
from vkapi.config import VK_CONFIG
from vkapi.exceptions import APIError


def get_posts_2500(
    owner_id: str = "",
    domain: str = "",
    offset: int = 0,
    count: int = 10,
    max_count: int = 2500,
    filter: str = "owner",
    extended: int = 0,
    fields: tp.Optional[tp.List[str]] = None,
) -> tp.Dict[str, tp.Any]:
    script = f"""
                var i = 0;
                var result = [];
                while i < {max_count} {{
                    result.push(
                                API.wall.get(
                                            {
                                            {
                                            f"owner_id: {owner_id}",
                                            f"domain: {domain}",
                                            f"offset: {offset} + i",
                                            f"count: {count}",
                                            f"filter: {filter}",
                                            f"extended: {extended}",
                                            f"fields: {fields}"    
                                            }
                                            }
                                            )
                                )
                    i = i + {count}
                }}return ;
            """
    data = {"code": script}
    response = session.post("/execute", data=data).json()["response"]
    return response["items"]


def get_wall_execute(
    owner_id: str = "",
    domain: str = "",
    offset: int = 0,
    count: int = 10,
    max_count: int = 2500,
    filter: str = "owner",
    extended: int = 0,
    fields: tp.Optional[tp.List[str]] = None,
    progress=None,
) -> pd.DataFrame:
    """
    Возвращает список записей со стены пользователя или сообщества.

    @see: https://vk.com/dev/wall.get

    :param owner_id: Идентификатор пользователя или сообщества, со стены которого необходимо получить записи.
    :param domain: Короткий адрес пользователя или сообщества.
    :param offset: Смещение, необходимое для выборки определенного подмножества записей.
    :param count: Количество записей, которое необходимо получить (0 - все записи).
    :param max_count: Максимальное число записей, которое может быть получено за один запрос.
    :param filter: Определяет, какие типы записей на стене необходимо получить.
    :param extended: 1 — в ответе будут возвращены дополнительные поля profiles и groups, содержащие информацию о пользователях и сообществах.
    :param fields: Список дополнительных полей для профилей и сообществ, которые необходимо вернуть.
    :param progress: Callback для отображения прогресса.
    """
    old_data = pd.DataFrame()
    code = f"""
            return API.wall.get ({{
            "owner_id": "{owner_id}",
            "domain": "{domain}",
            "offset": "0",
            "count": "1",
            "filter": "{filter}",
            "extended": "0",
            "fields": ""
}});
"""
    data = {"code": code}
    response = session.post("/execute", data=data).json()
    if "error" in response:
        raise APIError(response["error"]["error_msg"])
    if progress is None:
        progress = lambda x: x
    for _ in progress(
        range(0, math.ceil((response["response"]["count"] if count == 0 else count) / max_count))
    ):
        old_data = old_data.append(
            json_normalize(
                get_posts_2500(owner_id, domain, offset, count, max_count, filter, extended, fields)
            )
        )
        time.sleep(1)
    return old_data
