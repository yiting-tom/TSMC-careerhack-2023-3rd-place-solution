from dataclasses import dataclass
from dacite import from_dict

@dataclass
class Group:
    group_id: str

    def from_dict(dic: dict):
        return from_dict(Group, dic)
    
    def to_user_group_map(self):
        return {
            "group_group_id": self.group_id
        }

@dataclass
class GroupToAdd(Group):
    def from_rel_dict(dic: dict):
        return GroupToAdd(dic['group_id'])

@dataclass
class GroupToDelete(Group):
    ...