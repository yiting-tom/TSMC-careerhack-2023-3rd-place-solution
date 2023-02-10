#%%
from typing import List
import requests

from adapters.base import Querier, Creator, Deleter
from adapters.user import get_users_by_id
from models.dayoff import Dayoff, DayoffToAdd, DayoffToDelete
from utils import dict_to_objects


# @dict_to_objects(Dayoff)
def get_all_dayoffs() -> List[Dayoff]:
    """get_all_dayoffs

    Returns:
        List[Dayoff]: A list of dayoffs
    Example:
        >>> get_all_dayoffs()
        [
            Dayoff(
                dayoff_id=1,
                user=User(
                    user_id="user1",
                    email="user1@mail",
                    groups=["group1", "group2"]
                ),
                time='2023-02-09T22:07:13',
            ),
            ...
        ]
    """
    dayoffs = Querier("dayoff")\
        .query()
        
    for dayoff in dayoffs:
        dayoff["user"] = get_users_by_id(dayoff["user"]["user_id"])[0]
        dayoff["server"] = dayoff["server"]["server_id"]

    return dayoffs
    

@dict_to_objects(Dayoff)
def get_dayoff_between_datetime(from_datetime: str, to_datetime: str) -> List[Dayoff]:
    """get_dayoff_between_datetime

    Args:
        values (List[str]): A list of datetime

    Returns:
        List[Dayoff]: A list of dayoffs
    
    Example:
        >>> get_dayoff_between_datetime("2021-02-09T22:07:13", "2021-02-09T22:07:13")
        [
            Dayoff(
                dayoff_id=1,
                user=User(
                    user_id="user1",
                    email="user1@mail",
                    groups=["group1", "group2"]
                ),
                time='2023-02-09T22:07:13',
            ),
            Dayoff(
                dayoff_id=2,
                user=User(
                    user_id="user2",
                    email="user2@mail",
                    groups=["group2", "group3"]
                ),
                time='2023-02-19T22:07:13',
            ),
        ]
    """
    dayoffs = Querier("dayoff")\
        .filter_by("[time]", "between", [from_datetime, to_datetime])\
        .query()

    for dayoff in dayoffs:
        dayoff["user"] = get_users_by_id(dayoff["user"]["user_id"])[0]
        dayoff["server"] = dayoff["server"]["server_id"]

    return dayoffs

def get_day_of_by_user(values: List[str]) -> List[Dayoff]:
    """get_day_of_by_user

    Args:
        values (List[str]): A list of user_id

    Returns:
        List[Dayoff]: A list of dayoffs

    Example:
        >>> get_day_of_by_user("user1", "user2")
        [
            Dayoff(
                dayoff_id=1,
                user=User(
                    user_id="user1",
                    email="user1@mail",
                    groups=["group1", "group2"]
                ),
                time='2023-02-09T22:07:13',
            ),
            Dayoff(
                dayoff_id=2,
                user=User(
                    user_id="user2",
                    email="user2@mail",
                    groups=["group2", "group3"]
                ),
                time='2023-02-19T22:07:13',
            ),
        ]
    """
    dayoffs = Querier("dayoff")\
        .filter_by("[user][user_id]", "in", values)\
        .query()

    for dayoff in dayoffs:
        dayoff["user"] = get_users_by_id(dayoff["user"]["user_id"])[0]
        dayoff["server"] = dayoff["server"]["server_id"]
        
    return dayoffs

def add_one_dayoff(dayoff: DayoffToAdd) -> Dayoff:
    """add_one_dayoff

    Args:
        dayoff (DayoffToAdd): The dayoff to add

    Returns:
        Dayoff: The dayoff added

    Example:
        >>> add_one_dayoff(DayoffToAdd(
                user='user1',
                time='2023-02-09T22:07:13',
            ))
        <Response [200]>
    """
    add_new_dayoff = Creator("dayoff")
    return add_new_dayoff(dayoff)

def delete_one_dayoff(dayoff: DayoffToDelete) -> requests.Response:
    """delete_one_dayoff

    Args:
        dayoff (DayoffToDelete): The dayoff to delete

    Returns:
        requests.Response: The response from the API
    
    Example:
        >>> # if you have a dayoff with dayoff_id "test"
        >>> delete_one_dayoff(DayoffToDelete(dayoff_id="1"))
        <Response [200]>
        >>> # if you have no dayoff with dayoff_id "test"
        >>> delete_one_dayoff(DayoffToDelete(dayoff_id="1"))
        <Response [403]>
    """
    delete_exists_dayoff = Deleter("dayoff")
    return delete_exists_dayoff(dayoff.dayoff_id)
# %%
