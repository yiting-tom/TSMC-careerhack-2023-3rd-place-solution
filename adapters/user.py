#%%
import requests
from typing import List

from adapters.base import Querier, Creator, Deleter, Updater
from adapters.group import add_one_group, get_all_groups_map

from models.user import User, UserToAdd, UserToDelete, UserToUpdate
from models.group import GroupToAdd
from utils import dict_to_objects


@dict_to_objects(User)
def get_all_users() -> List[User]:
    """get_all_users

    Returns:
        List[User]: A list of users
    
    Example:
        >>> get_all_users()
        [
            User(
                user_id='user_id_1',
                email='user1@mail',
                groups=['group_id_1', 'group_id_2'],
            ),
            ...
        ]
    """
    users = Querier("user").query()
    return users

@dict_to_objects(User)
def get_users_by(column: str, keys: List[str]) -> List[User]:
    """get_users_by

    Args:
        column (str): the column to filter by
        keys (List[str]): the keys to filter by

    Returns:
        List[User]: A list of users
    
    Example:
        >>> get_users_by("user_id", ["user_id_1", "user_id_2"])
        [
            User(
                user_id='user_id_1',
                email='user1@mail',
                groups=['group_id_1', 'group_id_2'],
            ),
            User(
                user_id='user_id_2',
                email='user2@mail',
                groups=['group_id_1', 'group_id_3'],
            ),
        ]
    """
    users = Querier("user")\
        .filter_by(f"[{column}]", "in", keys)\
        .query()
    return users

def get_users_by_id(user_ids: List[str]) -> List[User]:
    """get_users_by_id 

    This function is implemented by calling get_users_by

    Args:
        user_ids (List[str]): a list of user ids

    Returns:
        List[User]: a list of users
    
    Example:
        >>> get_users_by_id(["user_id_1", "user_id_2"])
        [
            User(
                user_id='user_id_1',
                email='user1@mail',
                groups=['group_id_1', 'group_id_2'],
            ),
            User(
                user_id='user_id_2',
                email='user2@mail',
                groups=['group_id_1', 'group_id_3'],
            ),
        ]
    """
    return get_users_by("user_id", user_ids)

def get_users_by_email(emails: List[str]) -> List[User]:
    """get_users_by_id 

    This function is implemented by calling get_users_by

    Args:
        emails (List[str]): a list of emails

    Returns:
        List[User]: a list of users
    
    Example:
        >>> get_users_by_email(["user1@mail", "user2@mail"])
        [
            User(
                user_id='user_id_1',
                email='user1@mail',
                groups=['group_id_1', 'group_id_2'],
            ),
            User(
                user_id='user_id_2',
                email='user2@mail',
                groups=['group_id_1', 'group_id_3'],
            ),
        ]
    """
    return get_users_by("email", emails)

@dict_to_objects(User)
def get_users_by_groups(groups: List[str]) -> List[User]:
    """get_users_by_groups

    Args:
        groups (List[str]): a list of group ids

    Returns:
        List[User]: a list of users
    
    Example:
        >>> get_users_by_groups(["group_id_1", "group_id_3"])
        [
            User(
                user_id='user_id_1',
                email='user1@mail',
                groups=['group_id_1', 'group_id_2'],
            ),
            User(
                user_id='user_id_2',
                email='user2@mail',
                groups=['group_id_1', 'group_id_3'],
            ),
        ]
    """
    users = Querier("user")\
        .filter_by(
            field="[groups][group_group_id][group_id]",
            operator="in",
            values=groups)\
        .query()
    return users

def add_one_user(user: UserToAdd) -> requests.Response:
    """add_one_user

    When adding a user, we need to check if the groups the user belongs to
    already exist. If not, we add them first.

    Args:
        user (UserToAdd): The user to add

    Raises:
        ValueError: If the user already exists

    Returns:
        requests.Response: The response

    Example:
        >>> add_one_user(UserToAdd(
                email='user3@mail',
                groups=['group_id_2', 'group_id_3'],
            ))
        <Response [200]>
    """
    groups = get_all_groups_map()

    if user.groups:
        for group in user.groups:
            if group not in groups:
                add_one_group(GroupToAdd(group['group_group_id']))

    create_one_user = Creator("user")
    return create_one_user(user)

def delete_one_user(user: UserToDelete) -> requests.Response:
    """delete_one_user

    Args:
        user (UserToDelete): The user to delete

    Returns:
        requests.Response: The response
    
    Example:
        >>> delete_one_user(UserToDelete(user_id="user_id_1"))
        <Response [204]>
    """
    delete_one_user = Deleter("user")
    return delete_one_user(user.user_id)

def update_one_user(user: UserToUpdate) -> requests.Response:
    """update_one_user

    Args:
        user (UserToUpdate): The user to update

    Returns:
        requests.Response: The response

    Example:
        >>> update_one_user(UserToUpdate(
                user_id="user_id_1",
                email="user_1_new@mail",
            ))
        <Response [200]>
    """
    update_one_user = Updater("user")
    groups = get_all_groups_map()

    if user.groups:
        for group in user.groups:
            if group not in groups:
                add_one_group(GroupToAdd(group['group_group_id']))

    resp = update_one_user(user.user_id, user)
    return resp
