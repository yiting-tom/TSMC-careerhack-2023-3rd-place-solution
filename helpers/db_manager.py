""""
Copyright © Krypton 2019-2023 - https://github.com/kkrypt0nn (https://krypton.ninja)
Description:
🐍 A simple template to start to code your own and personalized discord bot in Python programming language.

Version: 5.5.0
"""

import os

import aiosqlite
from typing import List

DATABASE_PATH = f"{os.path.realpath(os.path.dirname(__file__))}/../database/database.db"


async def get_blacklisted_users() -> list:
    """
    This function will return the list of all blacklisted users.

    :param user_id: The ID of the user that should be checked.
    :return: True if the user is blacklisted, False if not.
    """
    async with aiosqlite.connect(DATABASE_PATH) as db:
        async with db.execute("SELECT user_id, strftime('%s', created_at) FROM blacklist") as cursor:
            result = await cursor.fetchall()
            return result


async def is_blacklisted(user_id: int) -> bool:
    """
    This function will check if a user is blacklisted.

    :param user_id: The ID of the user that should be checked.
    :return: True if the user is blacklisted, False if not.
    """
    async with aiosqlite.connect(DATABASE_PATH) as db:
        async with db.execute("SELECT * FROM blacklist WHERE user_id=?", (user_id,)) as cursor:
            result = await cursor.fetchone()
            return result is not None


async def add_user_to_blacklist(user_id: int) -> int:
    """
    This function will add a user based on its ID in the blacklist.

    :param user_id: The ID of the user that should be added into the blacklist.
    """
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("INSERT INTO blacklist(user_id) VALUES (?)", (user_id,))
        await db.commit()
        rows = await db.execute("SELECT COUNT(*) FROM blacklist")
        async with rows as cursor:
            result = await cursor.fetchone()
            return result[0] if result is not None else 0


async def remove_user_from_blacklist(user_id: int) -> int:
    """
    This function will remove a user based on its ID from the blacklist.

    :param user_id: The ID of the user that should be removed from the blacklist.
    """
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("DELETE FROM blacklist WHERE user_id=?", (user_id,))
        await db.commit()
        rows = await db.execute("SELECT COUNT(*) FROM blacklist")
        async with rows as cursor:
            result = await cursor.fetchone()
            return result[0] if result is not None else 0


async def add_warn(user_id: int, server_id: int, moderator_id: int, reason: str) -> int:
    """
    This function will add a warn to the database.

    :param user_id: The ID of the user that should be warned.
    :param reason: The reason why the user should be warned.
    """
    async with aiosqlite.connect(DATABASE_PATH) as db:
        rows = await db.execute("SELECT id FROM warns WHERE user_id=? AND server_id=? ORDER BY id DESC LIMIT 1", (user_id, server_id,))
        async with rows as cursor:
            result = await cursor.fetchone()
            warn_id = result[0] + 1 if result is not None else 1
            await db.execute("INSERT INTO warns(id, user_id, server_id, moderator_id, reason) VALUES (?, ?, ?, ?, ?)", (warn_id, user_id, server_id, moderator_id, reason,))
            await db.commit()
            return warn_id


async def remove_warn(warn_id: int, user_id: int, server_id: int) -> int:
    """
    This function will remove a warn from the database.

    :param warn_id: The ID of the warn.
    :param user_id: The ID of the user that was warned.
    :param server_id: The ID of the server where the user has been warned
    """
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("DELETE FROM warns WHERE id=? AND user_id=? AND server_id=?", (warn_id, user_id, server_id,))
        await db.commit()
        rows = await db.execute("SELECT COUNT(*) FROM warns WHERE user_id=? AND server_id=?", (user_id, server_id,))
        async with rows as cursor:
            result = await cursor.fetchone()
            return result[0] if result is not None else 0


async def get_warnings(user_id: int, server_id: int) -> list:
    """
    This function will get all the warnings of a user.

    :param user_id: The ID of the user that should be checked.
    :param server_id: The ID of the server that should be checked.
    :return: A list of all the warnings of the user.
    """
    async with aiosqlite.connect(DATABASE_PATH) as db:
        rows = await db.execute("SELECT user_id, server_id, moderator_id, reason, strftime('%s', created_at), id FROM warns WHERE user_id=? AND server_id=?", (user_id, server_id,))
        async with rows as cursor:
            result = await cursor.fetchall()
            result_list = []
            for row in result:
                result_list.append(row)
            return result_list


async def get_share_tags(server_id: int) -> list:
    """
    This function will get all the tags of a server.

    This funcion is for share command

    :param server_id: The ID of the server that should be checked.
    :return: A list of all the tags of the server.
    """
    async with aiosqlite.connect(DATABASE_PATH) as db:
        rows = await db.execute("SELECT DISTINCT tag FROM shares WHERE server_id=?", (server_id,))
        async with rows as cursor:
            result = await cursor.fetchall()
            result_list = []
            for row in result:
                result_list.append(row[0])
            return result_list


async def add_share(user_id: int, server_id: int, title: str, description: str, url: str, tag: str):
    """
    This function will add a share to the database.

    :param user_id: The ID of the user that should be added into the share.
    :param server_id: The ID of the server that should be added into the share.
    :param title: The title of the share.
    :param description: The description of the share.
    :param url: The url of the share.
    :param tag: The tag of the share.
    """
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("INSERT INTO shares(user_id, server_id, title, description, url, tag) VALUES (?, ?, ?, ?, ?, ?)", (user_id, server_id, title, description, url, tag,))
        await db.commit()

async def check_shares(user_id: int, server_id: int) -> list:
    """
    This function will check if a share exists.

    :param server_id: The ID of the server that should be checked.
    :param tag: The tag of the share that should be checked.
    :return: A list of all the shares of the server.
    """
    async with aiosqlite.connect(DATABASE_PATH) as db:
        rows = await db.execute("SELECT share_id, title, description, url, tag FROM shares WHERE user_id=? AND server_id=?", (user_id, server_id))
        async with rows as cursor:
            result = await cursor.fetchall()
            result_list = []
            for row in result:
                result_list.append(
                    {
                        "share_id": row[0],
                        "title": row[1],
                        "description": row[2],
                        "url": row[3],
                        "tag": row[4],
                    }
                )
            return result_list


async def delete_shares_by_share_ids(user_id: int, server_id: int, share_ids: List[str]):
    """
    Delect share from database by list of titles
    """
    async with aiosqlite.connect(DATABASE_PATH) as db:

        sql_cmd = "DELETE FROM shares WHERE user_id=? AND server_id=? AND share_id IN ({})".format(
            ','.join('?' * len(share_ids)))

        await db.execute(sql_cmd, (user_id, server_id, *share_ids,))
        await db.commit()


async def get_shares_by_tag(server_id: int, tag: str):
    """
    Get shares by tag
    """
    async with aiosqlite.connect(DATABASE_PATH) as db:
        rows = await db.execute("SELECT title, description, url, tag FROM shares WHERE server_id=? AND tag=?", (server_id, tag))
        async with rows as cursor:
            result = await cursor.fetchall()
            result_list = []
            for row in result:
                result_list.append(
                    {
                        "title": row[0],
                        "description": row[1],
                        "url": row[2],
                        "tag": row[3]
                    }
                )
            return result_list
