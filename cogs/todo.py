""""
Copyright © Krypton 2019-2023 - https://github.com/kkrypt0nn (https://krypton.ninja)
Description:
🐍 A simple template to start to code your own and personalized discord bot in Python programming language.

Version: 5.5.0
"""

import random
import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Context
from helpers import checks, db_manager
from discord.ext.forms import Form, Validator, ReactionForm, ReactionMenu
import adapters.todo as todo_adapter
from discord import ui


class TodoAddModal(ui.Modal):
    def __init__(self):
        super().__init__(timeout=60)

        self.add_item(ui.TextInput(
            label="Subject",
            required=True,
            max_length=255
        ))
        self.add_item(ui.TextInput(
            label="Description",
            required=False,
            style=discord.TextStyle.paragraph,
            max_length=255
        ))

    async def on_submit(self, interaction: discord.Interaction):
        subject = self.children[0].value
        description = self.children[1].value

        todo_adapter.add_todo(
            user_id=interaction.user.id,
            subject=subject,
            description=description,
        )

        await interaction.response.send_message("add todo", ephemeral=True)


async def to_int(ctx: commands.Context, message: discord.Message):
    """ Convert a message to an integer."""
    try:
        return int(message.content)
    except Exception as e:
        return False


async def to_sec(time_str: str):
    """ Convert a string to seconds.

    Examples:
        1s -> 1 second
        1m -> 60 seconds
        1h -> 3600 seconds
    """
    time_str = time_str.lower()
    times = time_str.split(" ")

    for t in times:
        if t[-1] not in ["s", "m", "h"]:
            raise Exception(f"Invalid time format {time_str}!")

    seconds = 0
    for t in times:
        if t[-1] == "s":
            seconds += int(t[:-1])
        elif t[-1] == "m":
            seconds += int(t[:-1]) * 60
        elif t[-1] == "h":
            seconds += int(t[:-1]) * 3600

    return seconds


async def check_duration(ctx: commands.Context, message: discord.Message):
    """ Check if the duration is valid."""
    try:
        sec = await to_sec(message.content)

        if sec < 1:
            return False
        return sec
    except Exception as e:
        return False


async def to_str(ctx: commands.Context, message: discord.Message):
    """ Convert a message to a string."""
    try:
        return str(message.content)
    except Exception as e:
        return False

# Here we name the cog and create a new class for the cog.


class Todo(commands.Cog, name="todo"):
    def __init__(self, bot):
        self.bot = bot

    # Here you can just add your own commands, you'll always need to provide "self" as first parameter.

    @commands.hybrid_group(
        name="todo",
        description="新增每日提醒",
    )
    # This will only allow non-blacklisted members to execute the command
    @checks.not_blacklisted()
    async def todo(self, context: Context):
        """
        This is a testing command that does nothing.

        :param context: The application command context.
        """
        if context.invoked_subcommand is None:
            embed = discord.Embed(
                description="Please specify a subcommand.\n \
                    ** Subcommands **\n \
                    `add` 新增事項到每日提醒\n \
                    `list` 檢視目前有哪些每日任務\n \
                    `delete` 刪除每日任務的事項\n \
                    `clear` 清空每日任務所有事項\n \
                    `set` 設定每日提醒的時間\n \
                    ",
                color=0xE02B2B
            )
            await context.send(embed=embed)

    @todo.command(
        name="add",
        description="新增事項到每日提醒",
    )
    @checks.not_blacklisted()
    async def todo_add(self, context: Context):
        """
        This is a testing command that does nothing.

        :param context: The application command context.
        """

        form = Form(context, '新增 todo', cleanup=False)
        form.add_question("標題", "subject", to_str)
        form.add_question("描述", "description", to_str)

        result = await form.start()

        print(result.subject)
        print(result.description)

        todo_adapter.add_todo(
            user_id=context.author.id,
            subject=result.subject,
            description=result.description,
        )

        embed = discord.Embed(
            title="成功新增 todo",
            color=0xE02B2B
        )

        embed.add_field(name="標題", value=result.subject, inline=False)
        embed.add_field(
            name="描述", value=result.description, inline=False)

        await context.send(embed=embed)


# And then we finally add the cog to the bot so that it can load, unload, reload and use it's content.
async def setup(bot):
    await bot.add_cog(Todo(bot))
