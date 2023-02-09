from dataclasses import dataclass
from dacite import from_dict

@dataclass
class Tag:
    tag_id: str

    def from_dict(dic: dict):
        return from_dict(Tag, dic)
    
    def to_share_tag_map(self):
        return {
            "tag_tag_id": self.tag_id
        }

@dataclass
class TagToAdd:
    tag_id: str

@dataclass
class TagToDelete:
    tag_id: str