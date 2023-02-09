from datetime import datetime
from dataclasses import dataclass
from models.user import User

@dataclass
class Dayoff:
    dayoff_id: int
    user: User
    time: datetime.timestamp
    def from_dict(dic: dict):
        return Dayoff(
            dayoff_id=dic['dayoff_id'],
            user=dic['user'],
            time=dic['time']
        )

@dataclass
class DayoffToAdd:
    user: User
    time: datetime.timestamp

@dataclass
class DayoffToUpdate:
    user_id: str
    time: datetime.timestamp

@dataclass
class DayoffToDelete:
    dayoff_id: int