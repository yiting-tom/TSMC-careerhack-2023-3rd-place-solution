from typing import Optional
from datetime import datetime
from dataclasses import dataclass
from models.user import User

@dataclass
class Todo:
    todo_id: int
    user: User
    subject: str
    description: Optional[str]
    def from_dict(dic: dict):
        return Todo(
            todo_id=dic['todo_id'],
            user=dic['user'],
            time=dic['time'],
            server_id=dic['server_id'],
            description=dic['description']
        )

@dataclass
class TodoToAdd:
    user: User
    subject: str
    description: Optional[str]

    def __init__(self, 
        user_id: str, 
        subject: str, 
        description: Optional[str]) -> None:

        self.user = {"user_id":user_id, "email": ""}
        self.subject = subject
        self.description = description

@dataclass
class TodoToDelete:
    todo_id: int

    def __init__(self, 
        todo_id: int) -> None:

        self.todo_id = todo_id