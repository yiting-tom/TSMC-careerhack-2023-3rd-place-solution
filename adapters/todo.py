#%%
from typing import List, Optional
import requests

from adapters.base import Querier, Creator, Deleter
from adapters.user import get_users_by_id, add_one_user
from models.todo import Todo, TodoToAdd, TodoToDelete
from models.user import User, UserToAdd, UserToDelete, UserToUpdate
from utils import dict_to_objects


def add_todo(user_id:str, subject:str, description:Optional[str]):
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
        user_to_add =  UserToAdd(
            user_id=todo.user["user_id"],
            email="",
            todo_time="8:00"
        )

        add_one_user(user_to_add)

    create_one_todo = Creator("todo")
    return create_one_todo(todo)

# %%
def delete_one_todo(todo: TodoToDelete):
    """ Delete a todo from the database."""

    delete_one_todo = Deleter("todo")
    return delete_one_todo(todo.todo_id)

# %%

# add_todo(
#     user_id="15551",
#     subject="Test",
#     description="Test",
# )


# %%


# t = TodoToDelete(
#     todo_id=2,
# )

# resp = delete_one_todo(t)
# # %%
# resp.text