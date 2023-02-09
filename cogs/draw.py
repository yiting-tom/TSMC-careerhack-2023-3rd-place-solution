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
import asyncio
import datetime


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


class Draw(commands.Cog, name="draw"):
    def __init__(self, bot):
        self.bot = bot

    # Here you can just add your own commands, you'll always need to provide "self" as first parameter.

    @commands.hybrid_group(
        name="draw",
        description="抽獎時間",
    )
    # This will only allow non-blacklisted members to execute the command
    @checks.not_blacklisted()
    async def draw(self, context: Context):
        """
        This is a testing command that does nothing.

        :param context: The application command context.
        """
        if context.invoked_subcommand is None:
            embed = discord.Embed(
                description="Please specify a subcommand.\n \
                    ** Subcommands **\n \
                    `add` 新增一個抽獎，點選表情來參加\n \
                    `all` 對群組內的所有人抽獎\n",
                color=0xE02B2B
            )
            await context.send(embed=embed)

    @draw.command(
        name="add",
        description="新增一個抽獎，點選表情來參加",
    )
    @checks.not_blacklisted()
    async def draw_add(self, context: Context):
        """
        This is a testing command that does nothing.

        :param context: The application command context.
        """

        form = Form(context, '⭐ 抽獎 ⭐', cleanup=False)
        form.edit_and_delete(False)
        form.set_retry_message('格式錯誤請重新輸入')
        form.add_question('你想要在哪個頻道開始抽獎?', 'channel', Validator('channel'))
        form.add_question('請輸入獎項', 'prize', to_str)
        form.add_question('請輸入抽獎時間\ne.g. 1h 30m 5s\n1m 30s',
                          'time', check_duration)
        form.add_question('請問要抽出幾個獎項?', 'number', to_int)

        form.set_timeout(30)
        await form.set_color("#7289DA")

        result = await form.start()

        # draw embed
        embed = discord.Embed(
            title="請點選 🎉 來參與抽獎",
            color=0xEAF506
        )

        loc_dt = datetime.datetime.now()
        time_del = datetime.timedelta(seconds=result.time)
        new_dt = loc_dt + time_del
        datetime_format = new_dt.strftime("%Y/%m/%d %H:%M:%S")

        embed.add_field(
            name=f"獎項", value=f"{result.prize} * {result.number}", inline=False)
        embed.add_field(
            name="抽獎公布時間", value=f"`{datetime_format}`", inline=False)
        embed.set_footer(text=f"抽獎由 {context.author} 發起")

        await context.channel.send(
            content=f"抽獎已開始，請到 {result.channel.mention} 參與抽獎！")

        msg = await result.channel.send(embed=embed, content="@everyone 抽獎開始!")
        await msg.add_reaction("🎉")
        await asyncio.sleep(result.time)

        msg = await result.channel.fetch_message(msg.id)

        reaction = msg.reactions[0]
        users = [user async for user in reaction.users()]

        if self.bot.user in users:
            users.pop(users.index(self.bot.user))

        if len(users) < result.number:
            await result.channel.send(f"參與人數小於 {result.number}，抽獎結束")
            return
        else:
            winners = random.sample(users, result.number)

            await result.channel.send(f"參與人數 {len(users)}\n恭喜 {', '.join([user.mention for user in winners])} 獲得 {result.prize}")

        await msg.clear_reactions()

    @draw.command(
        name="reset",
        description="test draw remove...",
    )
    @checks.not_blacklisted()
    async def draw_reset(self, context: Context):
        # Let's make our embed here...
        embed = discord.Embed(title="Reaction Menu Test",
                              description="Delete 5 messages?")
        # And send it! But we want to capture it as a variable!
        message = await context.send(embed=embed)
        # Initialize the reaction form...
        form = ReactionForm(message, self.bot, context.author)

        form.set_timeout(10)  # Set the timeout to 60 seconds.

        form.add_reaction("✅", 1)  # Add the ✅ reaction which will return 1.
        form.add_reaction("❌", 2)  # Add the ❌ reaction which will return 2.
        form.add_reaction("🤷", 3)  # Add the 🤷 reaction which will return 3.

        # Start the form! Choice will be True or False based on the input.
        choice = await form.start()

        await context.send(f"You chose {choice}!")  # Send the choice!

    @draw.command(
        name="menu",
        description="test draw remove...",
    )
    @checks.not_blacklisted()
    async def draw_menu(self, ctx):

        jokes = ["有時候也很佩服自己，明明薪水這麼少，卻能把自己養這麼胖。", "母雞向母牛抱怨：「真受不了人類，他們每天用盡方法避孕，卻讓我們下蛋！」母牛回答：「那算什麼！他們每天喝我的奶，卻沒人叫我一聲媽咪。」",
                 "媽媽指著食人魚跟女兒說：「女兒，你看，這是會吃人的魚。」而食人魚媽媽則跟食人魚女兒說：「女兒，你看，這是會吃魚的人。」", "你知道天上的星星一顆有多重嗎？ 答案就是八公克．．．．．．．．．．．因為 星巴克！", "朋友問我說情人節我還是一個人嗎？廢話！難道我會變成一條狗嗎？"]

        embed_list = [
            discord.Embed(title=f"Joke {i+1}", description=j, color=0x00ff00) for i, j in enumerate(jokes)
        ]

        rmenu = ReactionMenu(ctx, embed_list)
        await rmenu.start()

    @draw.command(
        name="all",
        description="對群組內的所有人抽獎",
    )
    @checks.not_blacklisted()
    async def draw_all(self, context: Context):
        """ Get all members and start draw """

        form = Form(context, '⭐ 抽獎 ⭐', cleanup=False)
        form.add_question('請輸入獎項', 'prize', to_str)
        form.add_question('請問要抽出幾個獎項?', 'number', to_int)

        result = await form.start()

        guild = context.guild
        members = [m for m in guild.members if m.bot == False]

        winners = random.sample(members, result.number)

        await context.channel.send(f"恭喜 {', '.join([user.mention for user in winners])} 獲得 {result.prize}")


# And then we finally add the cog to the bot so that it can load, unload, reload and use it's content.
async def setup(bot):
    await bot.add_cog(Draw(bot))
