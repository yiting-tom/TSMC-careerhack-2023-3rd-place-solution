# %%
import requests
from typing import List, Set

from adapters.base import Querier, Creator, Deleter, API_URL
from adapters.tag import add_one_tag, get_all_tags_map
from adapters.user import get_users_by_id

from models.share import Share, ShareToAdd, ShareToDelete
from adapters.tag import get_tag_id_by_map_id
from models.tag import TagToAdd 
from utils import dict_to_objects
from utils.logger import L
from models.base import QueryRule
import requests


@dict_to_objects(Share)
def get_all_shares() -> List[Share]:
    """get_all_shares

    Returns:
        List[Share]: A list of shares

    Example:
        >>> get_all_shares()
        [
            Share(
                share_id='share_id_1',
                server_id='server_id_1',
                title='share1 title',
                description='share1 description',
                user='share1 url',
                user=User(
                    "user_id": "user_id_1",
                    "email": "user1@mail",
                    "groups": ["group_1", "group_2"],
                )
                tags=['tag_1', 'tag_2'],
            ),
            ...
        ]
    """
    shares = Querier("share").query()

    for share in shares:
        share["user"] = get_users_by_id(share["user"]["user_id"])[0]
        share["server"] = share["server"]["server_id"]

    return shares


def get_shares_by(column: str, keys: List[str]) -> List[Share]:
    """get_shares_by

    Args:
        column (str): the column to filter by
        keys (List[str]): the keys to filter by

    Returns:
        List[Share]: A list of shares

    Example:
        >>> get_shares_by("user", ["user_id_1", "user_id_2"])
        [
            Share(
                share_id='share_id_1',
                server_id='server_id_1',
                title='share1 title',
                description='share1 description',
                url='share1 url',
                user=User(
                    "user_id": "user_id_1",
                    "email": "user1@mail",
                    "groups": ["group_id_1", "group_id_2"],
                )
                tags=['tag_id_1', 'tag_id_2'],
            ),
            Share(
                share_id='share_id_2',
                server_id='server_id_1',
                title='share2 title',
                description='share2 description',
                user='share2 url',
                user=User(
                    "user_id": "user_id_1",
                    "email": "user1@mail",
                    "groups": ["group_id_1", "group_id_2"],
                )
                tags=['tag_id_2'],
            ),
        ]
    """
    shares = Querier("share")\
        .filter_by(f"[{column}]", "in", keys)\
        .query()

    for share in shares:
        share["user"] = get_users_by_id(share["user"]["user_id"])[0]
        share["server"] = share["server"]["server_id"]

    return shares


@dict_to_objects(Share)
def get_shares_by_rules(rules: List[QueryRule]) -> List[Share]:
    share_querier = Querier("share")

    for rule in rules:
        share_querier = share_querier.filter_by(
            rule.column, rule.operator, rule.value)

    shares = share_querier.query()

    for share in shares:
        share["user"] = get_users_by_id(share["user"]["user_id"])[0]
        share["server"] = share["server"]["server_id"]

    return shares


def get_shares_by_tags(tags: List[str]) -> List[Share]:
    """get_shares_by_tags

    Args:
        tags (List[str]): a list of tag ids

    Returns:
        List[Share]: a list of shares

    Example:
        >>> get_shares_by_tags(["tag_id_2"])
        [
            Share(
                share_id='share_id_1',
                server_id='server_id_1',
                title='share1 title',
                description='share1 description',
                url='share1 url',
                user=User(
                    "user_id": "user_id_1",
                    "email": "user1@mail",
                    "groups": ["group_id_1", "group_id_2"],
                )
                tags=['tag_id_1', 'tag_id_2'],
            ),
            Share(
                share_id='share_id_2',
                server_id='server_id_1',
                title='share2 title',
                description='share2 description',
                user='share2 url',
                user=User(
                    "user_id": "user_id_1",
                    "email": "user1@mail",
                    "groups": ["group_id_1", "group_id_2"],
                )
                tags=['tag_id_2'],
            ),
        ]
    """
    shares = Querier("share")\
        .filter_by(
            field="[tags][tag_tag_id][tag_id]",
            operator="in",
            values=tags)\
        .query()

    for share in shares:
        share["user"] = get_users_by_id(share["user"]["user_id"])[0]
        share["server"] = share["server"]["server_id"]

    return shares


def add_one_share(share: ShareToAdd) -> requests.Response:
    """add_one_share

    When adding a share, we need to check if the tags the share belongs to
    already exist. If not, we add them first.

    Args:
        share (ShareToAdd): The share to add

    Raises:
        ValueError: If the share already exists

    Returns:
        requests.Response: The response

    Example:
        >>> add_one_share(ShareToAdd(
                title='share1 title',
                user_id='user_id_1',
                description='share1 description',
                url='share1 url',
                user="user_id_1",
                tags=['tag_id_1', 'tag_id_2'],
            ))
        <Response [200]>
    """
    tags = get_all_tags_map()

    if share.tags:
        for tag in share.tags:
            if tag not in tags:
                add_one_tag(TagToAdd(tag['tag_tag_id']))

    create_one_share = Creator("share")
    return create_one_share(share)


def delete_one_share(share: ShareToDelete) -> requests.Response:
    """delete_one_share

    Args:
        share (ShareToDelete): The share to delete

    Returns:
        requests.Response: The response

    Example:
        >>> delete_one_share(ShareToDelete(share_id="share_id_1"))
        <Response [204]>
    """
    delete_one_share = Deleter("share")
    return delete_one_share(share.share_id)


def get_share_tags_by_server_id(server_id: str) -> Set[str]:
    """
    This function will get all the tags of a server.

    This funcion is for share command

    :param server_id: The ID of the server that should be checked.
    :return: A list of all the tags of the server.
    """
    server_id = str(server_id)
    url = f"{API_URL}/items/share?fields[]=tags.tag_tag_id.tag_id&filter[server][_eq]={server_id}"
    resp = requests.get(url).json()['data']

    result = []

    for r in resp:
        result.extend(r['tags'])

    result = set([r['tag_tag_id']['tag_id'] for r in result])

    return result


def add_share(user_id: str, server_id: str, title: str, description: str, url: str, tags: List[str]):
    """
    This function will add a share to the database.

    :param user_id: The ID of the user that should be added into the share.
    :param server_id: The ID of the server that should be added into the share.
    :param title: The title of the share.
    :param description: The description of the share.
    :param url: The url of the share.
    :param tag: The tag of the share.
    """
    
    user_id = str(user_id)
    server_id = str(server_id)
    title = str(title)
    description = str(description)
    url = str(url)
    tags = [str(tag) for tag in tags]

    share = ShareToAdd(
        user_id=user_id,
        server_id=server_id,
        title=title,
        description=description,
        url=url,
        tags=tags
    )

    add_one_share(share)

def delete_shares_by_share_ids(share_ids: List[str]):
    """
    Delect share from database by list of titles
    """

    share_ids = [str(share_id) for share_id in share_ids]

    for share_id in share_ids:
        delete_one_share(ShareToDelete(share_id=share_id))