from typing import Optional
from datetime import datetime
from dataclasses import dataclass
from models.user import User

@dataclass
class Dayoff:
    dayoff_id: int
    server_id: str
    user: User
    description: Optional[str]
    time: datetime.timestamp
    server_id: str
    description: Optional[str]
    def from_dict(dic: dict):
        return Dayoff(
            dayoff_id=dic['dayoff_id'],
            user=dic['user'],
            time=dic['time'],
            server_id=dic['server_id'],
            description=dic['description']
        )

@dataclass
class DayoffToAdd:
    user: str
    server: str
    time: datetime.timestamp
    description: Optional[str]

    def __init__(self, 
        user_id: str, 
        server_id: str, 
        time: datetime.timestamp, 
        description: Optional[str]) -> None:
        self.user = {"user_id":user_id} # user object to user_id
        self.server = {"server_id": server_id}
        self.server_id = server_id
        self.time = time
        self.description = description


@dataclass
class DayoffToUpdate:
    user_id: str
    time: datetime.timestamp
    dayoff_id: int

    def __init__(self, 
        time: Optional[datetime.timestamp], 
        description: Optional[str],
        dayoff_id: int
        ) -> None:

        self.time = time
        self.description = description
        self.dayoff_id = dayoff_id

@dataclass
class DayoffToDelete:
    dayoff_id: int