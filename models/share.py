from typing import Optional, List
from dacite import from_dict

from dataclasses import dataclass
from models.user import User

@dataclass
class Share:
    share_id: int
    server: str
    user: User
    title: str
    description: Optional[str] = None
    url: Optional[str] = None
    tags: List[str] = None

    def from_dict(dic: dict):
        tag_ids = []
        if "tags" in dic:
            for tag in dic['tags']:
                tag_ids.append(tag['tag_tag_id'])
            dic['tags'] = tag_ids
        
        return from_dict(Share, dic)

@dataclass
class ShareToAdd:
    user: User
    server_id: str
    title: str
    description: Optional[str] = None
    url: Optional[str] = None
    tags: List[str] = None
    def __init__(
        self,
        user_id: str,
        server_id: str,
        title: str,
        description: Optional[str] = None,
        url: Optional[str] = None,
        tags: Optional[List[str]] = None
    ):
        self.user = {"user_id": user_id}
        self.server_id = server_id
        self.title = title
        self.description = description
        self.url = url
        self.tags = [{"tag_tag_id": tag} for tag in tags] if tags else None


@dataclass
class ShareToDelete:
    share_id: int