#%%
from typing import List
import requests

from adapters.base import Querier, Creator, Deleter
from models.tag import Tag, TagToAdd, TagToDelete
from utils import dict_to_objects


@dict_to_objects(Tag)
def get_all_tags() -> List[Tag]:
    """get_all_tags

    Returns:
        List[Tag]: A list of tags
    """
    tags = Querier("tag")\
        .query()
    return tags

def get_all_tags_map() -> List[dict]:
    """get_all_tags_map

    the function is used to get all tags with only the tag_id
    and should only be used for user creation and update scenarios.

    the return format will be like:
    ::
        [
            {"tag_tag_id": "tag_id_1"},
            {"tag_tag_id": "tag_id_2"},
            ...
        ]

    Returns:
        List[Tag]: A list of tags with only the tag_id
    """
    tags = Querier("tag")\
        .query()
    return [{'tag_tag_id': tag['tag_id']} for tag in tags]

def add_one_tag(tag: TagToAdd) -> Tag:
    """add_one_tag

    Args:
        tag (TagToAdd): The tag to add

    Returns:
        Tag: The tag added
    """
    add_new_tag = Creator("tag")
    return add_new_tag(tag)

def delete_one_tag(tag: TagToDelete) -> requests.Response:
    """delete_one_tag

    Args:
        tag (TagToDelete): The tag to delete

    Returns:
        requests.Response: The response from the API
    
    Example:
        >>> # if you have a tag with tag_id "test"
        >>> delete_one_tag(TagToDelete(tag_id="test"))
        <Response [200]>
        >>> # if you have no tag with tag_id "test"
        >>> delete_one_tag(TagToDelete(tag_id="test"))
        <Response [403]>
    """
    delete_exists_tag = Deleter("tag")
    return delete_exists_tag(tag.tag_id)