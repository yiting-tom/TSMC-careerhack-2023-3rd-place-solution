""""
Copyright © Krypton 2019-2023 - https://github.com/kkrypt0nn (https://krypton.ninja)
Description:
🐍 A simple template to start to code your own and personalized discord bot in Python programming language.

Version: 5.5.0
"""

import discord
from discord import app_commands
from discord.ext import tasks, commands
from discord.ext.commands import Context

from helpers import checks,db_manager


# Here we name the cog and create a new class for the cog.
class Attend(commands.Cog, name="attend"):
    def __init__(self, bot):
        self.bot = bot
        self.send_attend.start()

    @tasks.loop(seconds=5.0)
    async def send_attend(self) -> None:
        channel = self.bot.get_channel(1070990736511746109)
        message = await channel.send(f'Test pininggggggggggg!')
        await message.pin()

    @commands.hybrid_group(
        name="dayoff",
        description="Take day off for user.",
    )
    @checks.not_blacklisted()
    async def dayoff(self, context: Context) -> None :
        """
        Lets you take a day off or cancel the day off.

        :param context: The hybrid command context.
        """
        if context.invoked_subcommand is None:
            embed = discord.Embed(
                description="You need to specify a subcommand.\n\n**Subcommands:**\n`show` - Show the days-off\n`add` - Take a day off.\n`cancel` - Cancel the day off.",
                color=0xE02B2B
            )
            await context.send(embed=embed)

    @dayoff.command(
        base="dayoff",
        name="show",
        description="Show the list of day off.",
    )
    @checks.not_blacklisted()
    async def dayoff_show(self, context: Context) -> None:
        """
        Shows the list of day off users.

        :param context: The hybrid command context.
        """
        dayoff_users = await db_manager.get_dayoff_users()
        if len(dayoff_users) == 0:
            embed = discord.Embed(
                description="There are currently no day off users.",
                color=0xE02B2B
            )
            await context.send(embed=embed)
            return

        embed = discord.Embed(
            title="days-off for Users",
            color=0x9C84EF
        )
        users = []
        for bluser in dayoff_users:
            user = self.bot.get_user(int(bluser[0])) or await self.bot.fetch_user(int(bluser[0]))
            users.append(
                f"• {user.mention} ({user}) - Day off in *{bluser[1]}*")
        embed.description = "\n".join(users)
        await context.send(embed=embed)

    @dayoff.command(
        base="dayoff",
        name="add",
        description="Take a day off in some day.",
    )
    @checks.not_blacklisted()
    @app_commands.describe(user="The user that take a day off")
    async def dayoff_add(self, context: Context, user: discord.User, date: str) -> None:
        """
        Lets you take a day off.

        :param context: The hybrid command context.
        :param user: The user that should be added to the day-off list.
        """
        user_id = user.id
        total = await db_manager.add_user_to_dayoff(user_id, date)
        embed = discord.Embed(
            description=f"**{user.name}** has been successfully taked a day off.",
            color=0x9C84EF
        )
        await context.send(embed=embed)

    @dayoff.command(
        base="dayoff",
        name="cancel",
        description="Cancel the day off in some day.",
    )
    @checks.not_blacklisted()
    async def dayoff_cancel(self, context: Context, user: discord.User, date: str) -> None:
        """
        Lets you cancel the days-odd from day-off list.

        :param context: The hybrid command context.
        :param user: The user that should be removed from the blacklist.
        """
        user_id = user.id
        if not await db_manager.in_day_off_list(user_id, date):
            embed = discord.Embed(
                description=f"**{user.name}** have not request for days-off.",
                color=0xE02B2B
            )
            await context.send(embed=embed)
            return
        total = await db_manager.remove_user_from_dayoff(user_id, date)
        embed = discord.Embed(
            description=f"**{user.name}** has been successfully canceled day-off",
            color=0x9C84EF
        )
        embed.set_footer(
            text=f"There {'is' if total == 1 else 'are'} now {total} {'user' if total == 1 else 'users'} in the day-off list"
        )
        await context.send(embed=embed)

# And then we finally add the cog to the bot so that it can load, unload, reload and use it's content.
async def setup(bot):
    await bot.add_cog(Attend(bot))
