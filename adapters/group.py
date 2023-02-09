#%%
from typing import List
import requests

from adapters.base import Querier, Creator, Deleter
from models.group import Group, GroupToAdd, GroupToDelete
from utils import dict_to_objects


@dict_to_objects(Group)
def get_all_groups() -> List[Group]:
    """get_all_groups

    Returns:
        List[Group]: A list of groups
    """
    groups = Querier("group")\
        .query()
    return groups

def get_all_groups_map() -> List[dict]:
    """get_all_groups_map

    the function is used to get all groups with only the group_id
    and should only be used for user creation and update scenarios.

    the return format will be like:
    ::
        [
            {"group_group_id": "group_id_1"},
            {"group_group_id": "group_id_2"},
            ...
        ]

    Returns:
        List[Group]: A list of groups with only the group_id
    """
    groups = Querier("group")\
        .query()
    return [{'group_group_id': group['group_id']} for group in groups]

def add_one_group(group: GroupToAdd) -> Group:
    """add_one_group

    Args:
        group (GroupToAdd): The group to add

    Returns:
        Group: The group added
    """
    add_new_group = Creator("group")
    return add_new_group(group)

def delete_one_group(group: GroupToDelete) -> requests.Response:
    """delete_one_group

    Args:
        group (GroupToDelete): The group to delete

    Returns:
        requests.Response: The response from the API
    
    Example:
        >>> # if you have a group with group_id "test"
        >>> delete_one_group(GroupToDelete(group_id="test"))
        <Response [200]>
        >>> # if you have no group with group_id "test"
        >>> delete_one_group(GroupToDelete(group_id="test"))
        <Response [403]>
    """
    delete_exists_group = Deleter("group")
    return delete_exists_group(group.group_id)
