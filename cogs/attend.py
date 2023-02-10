""""
Copyright © Krypton 2019-2023 - https://github.com/kkrypt0nn (https://krypton.ninja)
Description:
🐍 A simple template to start to code your own and personalized discord bot in Python programming language.

Version: 5.5.0
"""
from datetime import datetime, timedelta

import discord
from discord import app_commands
from discord.ext import tasks, commands
from discord.ext.commands import Context
from discord import ui

from adapters.dayoff import get_all_dayoffs, get_user_in_date, add_one_dayoff, get_dayoff_after_today, get_dayoff_by_user_and_server, delete_dayoff, get_user_by_server_and_date
from helpers import checks

from models.dayoff import DayoffToAdd


class ButtonCheck(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None

    @discord.ui.button(label="⭕", style=discord.ButtonStyle.blurple)
    async def confirm(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.value = "yes"
        self.stop()

    @discord.ui.button(label="❌", style=discord.ButtonStyle.blurple)
    async def cancel(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.value = "no"
        self.stop()


class DayoffAddModal(ui.Modal):
    def __init__(self, title, select_values="新增請假資訊", **kwargs):

        super().__init__(title=title)

        self.add_item(ui.TextInput(
            label="Date",
            required=True,
            max_length=255,
            placeholder="YY-MM-DD format e.g. `2023-02-01`"
        ))
        self.add_item(ui.TextInput(
            label="Description",
            required=False,
            max_length=255,
            style=discord.TextStyle.paragraph
        ))

    async def on_submit(self, interaction: discord.Interaction):

        user_id = interaction.user.id
        server_id = interaction.guild.id
        date = self.children[0].value
        description = self.children[1].value
        today = datetime.today()

        if datetime.strptime(date, "%Y-%m-%d") < today - timedelta(days=1):
            embed = discord.Embed(
                description=f"請不要輸入今天之前的日期！！",
                color=0xE02B2B
            )
            await interaction.response.send_message(embed=embed)
            return

        # if await db_manager.in_day_off_list(user_id, server_id, date):
        if get_user_in_date(str(user_id), str(server_id), date):
            embed = discord.Embed(
                description=f"**{interaction.user.name}** 已經在 **{date}** 提出請假申請",
                color=0xE02B2B
            )
            await interaction.response.send_message(embed=embed)
            return

        embed = discord.Embed(
            description=f"**{interaction.user.name}** 請假成功!!  日期： **{date}**",
            color=0x9C84EF
        )


        # await db_manager.add_user_to_dayoff(
        #     user_id=user_id,
        #     server_id = server_id,
        #     date=date,
        #     description = description
        # )
        add_one_dayoff(DayoffToAdd(
            user_id=str(user_id),
            server_id=str(server_id),
            time=date,
            description=description
        ))

        await interaction.response.send_message(embed=embed)


class DayoffView(discord.ui.View):

    @discord.ui.button(label="輸入請假資訊", style=discord.ButtonStyle.blurple)
    async def button_callback(self, interaction, button):
        await interaction.response.send_modal(
            DayoffAddModal(title="請假資訊")
        )


# Here we name the cog and create a new class for the cog.


class Attend(commands.Cog, name="attend"):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_group(
        name="dayoff",
        description="Take day off for user.",
    )
    @checks.not_blacklisted()
    async def dayoff(self, context: Context) -> None:
        """
        Lets you take a day off or cancel the day off.

        :param context: The hybrid command context.
        """
        if context.invoked_subcommand is None:
            embed = discord.Embed(
                description="You need to specify a subcommand.\n\n**Subcommands:**\n`show` - Show the days-off\n`add` - Take a day off.\n`cancel` - Cancel the day off.\n`today` - Show the attendance today.",
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
        Shows the all list of day off users.

        :param context: The hybrid command context.
        """
        # dayoff_users = await db_manager.get_dayoff_users()
        dayoff_users = get_dayoff_after_today()

        if len(dayoff_users) == 0:
            embed = discord.Embed(
                description="目前沒有人請假",
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
            print(bluser)
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
    async def dayoff_add(self, context: Context) -> None:
        """
        Lets you take a day off.

        :param context: The hybrid command context.
        :param user: The user want to request a day off.
        """
        if context.guild is None:
            await context.send("This function can only be used in a server.")
            return

        await context.send(view=DayoffView())

    @dayoff.command(
        base="dayoff",
        name="cancel",
        description="Cancel the day off in some day.",
    )
    @checks.not_blacklisted()
    async def dayoff_cancel(self, context: Context) -> None:
        """
        Lets you cancel the days-off from day-off list.

        :param context: The hybrid command context.
        :param user: The user that want to cancel day off.
        """
        if context.guild is None:
            await context.send("This function can only be used in a server.")
            return

        # dayoffs = await db_manager.check_dayoff(
        #     user_id=context.author.id,
        #     server_id=context.guild.id,
        # )
        dayoffs = get_dayoff_by_user_and_server(
            user_id=str(context.author.id),
            server_id=str(context.guild.id),
        )

        if len(dayoffs) == 0:
            embed = discord.Embed(
                description="您目前沒有提出請假申請",
                color=0xE02B2B
            )
            await context.send(embed=embed)
            return

        options = [
            discord.SelectOption(label="取消", value="cancel")
        ]

        options.extend([
            discord.SelectOption(
                label=dayoff,
                value=dayoff
            )
            for dayoff in dayoffs
        ])

        view = ui.View()
        select_ui = ui.Select(
            placeholder="請選擇要刪除的分享",
            options=options,
            min_values=1,
            max_values=max(len(options), 1)
        )

        async def callback(interaction: discord.Interaction):

            embed = discord.Embed(
                    title="刪除成功",
                    color=0x9C84EF
                )

            date = select_ui.values[0]

            if "cancel" in date:
                await interaction.message.edit(content="取消刪除", view=None, embed=embed)
                return

            double_check_ui = ButtonCheck()

            await interaction.response.edit_message(content=f"確認刪除?", view=double_check_ui)
            await double_check_ui.wait()

            if double_check_ui.value == "yes":
                delete_dayoff(
                    user_id=context.author.id,
                    server_id=context.guild.id,
                    date=date
                )
                await interaction.message.edit(content="刪除成功", view=None, embed=embed)
            elif double_check_ui.value == "no":
                await interaction.message.edit(content="取消刪除", view=None, embed=embed)

            double_check_ui.stop()

        select_ui.callback = callback
        view.add_item(select_ui)

        await context.send(view=view)

    @dayoff.command(
        base="dayoff",
        name="today",
        description="Display attendance and pin it.",
    )
    @checks.not_blacklisted()
    async def today(self, context: Context) -> None:
        """
        Show the all days-off today.

        :param context: The hybrid command context.
        :param user: The user that want to display day off today.
        """
        today = datetime.now().strftime("%Y-%m-%d")
        dayoff_users = get_user_by_server_and_date(server_id=context.guild.id, date=today)

        if len(dayoff_users) == 0:
            embed = discord.Embed(
                description="今天沒有人請假",
                color=0xE02B2B
            )
            message = await context.send(embed=embed)
            await message.pin()
            return

        embed = discord.Embed(
            title=f"**{today}**  請假名單",
            color=0x9C84EF
        )
        users = []
        for bluser in dayoff_users:
            user = self.bot.get_user(int(bluser[0])) or await self.bot.fetch_user(int(bluser[0]))
            users.append(
                f"• {user.mention} ({user})")
        embed.description = "\n".join(users)
        message = await context.send(embed=embed)
        await message.pin()


# And then we finally add the cog to the bot so that it can load, unload, reload and use it's content.


async def setup(bot):
    await bot.add_cog(Attend(bot))
