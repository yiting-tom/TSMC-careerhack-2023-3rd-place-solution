from typing import List, Optional
from dataclasses import dataclass

from dacite import from_dict


@dataclass
class User:
    user_id: str
    email: str
    groups: List[str]

    def from_dict(dic: dict):
        group_ids = []
        if "groups" in dic:
            for group in dic['groups']:
                group_ids.append(group['group_group_id'])
            dic['groups'] = group_ids
        
        return from_dict(User, dic)

@dataclass
class UserToAdd:
    user_id: str
    email: str
    groups: Optional[List[str]] = None

    def __init__(
        self,
        user_id: str,
        email: str,
        groups: Optional[List[str]] = None
    ):
        self.user_id = user_id
        self.email = email
        self.groups = [{"group_group_id": group} for group in groups] if groups else None

@dataclass
class UserToDelete:
    user_id: str

@dataclass
class UserToUpdate:
    user_id: str
    email: Optional[str] = None
    groups: Optional[List[str]] = None

    def __init__(
        self,
        user_id: str,
        email: Optional[str] = None,
        groups: Optional[List[str]] = None
    ):
        self.user_id = user_id
        self.email = email
        self.groups = [{"group_group_id": group} for group in groups] if groups else None
