import datetime as dt
import statistics
import typing as tp

from vkapi.friends import get_friends #type: ignore


def age_predict(user_id=320832582) -> tp.Optional[float]:
    """
    Наивный прогноз возраста пользователя по возрасту его друзей.

    Возраст считается как медиана среди возраста всех друзей пользователя

    :param user_id: Идентификатор пользователя.
    :return: Медианный возраст пользователя.
    """
    age = []
    this = dt.date.today()
    friends = get_friends(user_id, fields=["bdate"]).items
    for friend in friends:
        try:
            bdate = dt.datetime.strptime(friend["bdate"], "%d.%m.%Y")  # type: ignore
        except (KeyError, ValueError):
            continue
        age.append(
            this.year
            - bdate.year
            - (this.month < bdate.month or (this.month == bdate.month and this.day < bdate.day))
        )

    if age:
        return statistics.median(age)
    return None