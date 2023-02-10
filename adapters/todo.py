# %%
from typing import List, Optional
import requests
from adapters.base import Querier, Creator, Deleter, API_URL
from adapters.user import get_users_by_id, add_one_user
from models.todo import Todo, TodoToAdd, TodoToDelete
from models.user import UserToAdd, UserToUpdate
import adapters.user as user_adapter
from utils import dict_to_objects
from datetime import datetime

def add_todo(user_id: str, subject: str, description: Optional[str]):
    """ Add a todo to the database."""

    user_id = str(user_id)
    subject = str(subject)

    todo_to_add = TodoToAdd(
        user_id=user_id,
        subject=subject,
        description=description,
    )

    return add_one_todo(todo_to_add)


def add_one_todo(todo: TodoToAdd):
    """ Add a todo to the database."""

    if len(get_users_by_id(todo.user["user_id"])) == 0:
        user_to_add = UserToAdd(
            user_id=todo.user["user_id"],
            email="",
            todo_time="8:00"
        )

        add_one_user(user_to_add)

    create_one_todo = Creator("todo")
    return create_one_todo(todo)

def delete_one_todo(todo: TodoToDelete):
    """ Delete a todo from the database."""

    delete_one_todo = Deleter("todo")
    return delete_one_todo(todo.todo_id)


def delete_todo_by_ids(todo_ids: List[int]):
    """ Delete a todo from the database."""

    for todo_id in todo_ids:
        delete_one_todo = Deleter("todo")
        delete_one_todo(todo_id)


def get_todos(user_id: str) -> List[Todo]:
    """ Get user's all todos from the database."""

    user_id = str(user_id)

    api = f"{API_URL}/items/todo?filter[user][_eq]={user_id}"

    todos = requests.get(api).json()["data"]

    return todos


def set_remind_time(user_id: str, remind_time: str):
    """ Set user's remind time."""

    user_id = str(user_id)
    remind_time = str(remind_time)

    user_to_update = UserToUpdate(
        user_id=user_id,
        todo_time=remind_time
    )

    user_adapter.update_one_user(user_to_update)


def get_todos_by_remind_time(remind_time: str) -> List[Todo]:
    """ Get user's all todos from the database."""

    api = f"{API_URL}/items/user?filter[todo_time][_eq]={remind_time}"

    todos = requests.get(api).json()["data"]

    return todos