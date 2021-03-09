# pylint: disable=missing-function-docstring
# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=unused-argument
# pylint: disable=unused-import
# pylint: disable=too-many-arguments
# pylint: disable=redefined-builtin

import datetime as dt
import statistics
import typing as tp

from vkapi.friends import get_friends


def age_predict(user_id: int) -> tp.Optional[float]:
    """
    Наивный прогноз возраста пользователя по возрасту его друзей.

    Возраст считается как медиана среди возраста всех друзей пользователя

    :param user_id: Идентификатор пользователя.
    :return: Медианный возраст пользователя.
    """
    friends = get_friends(user_id, fields=["bdate"]).items
    years_of_birth = []
    for friend in friends:
        try:
            bdate = dt.datetime.strptime(friend["bdate"], "%d.%m.%Y")  # type: ignore
        except (KeyError, ValueError):
            continue
        years_of_birth.append(dt.datetime.now().year - bdate.year)
    if years_of_birth:
        return float(statistics.median(years_of_birth))
    return None
