""""
Copyright © Krypton 2019-2023 - https://github.com/kkrypt0nn (https://krypton.ninja)
Description:
🐍 A simple template to start to code your own and personalized discord bot in Python programming language.

Version: 5.5.0
"""
import discord
import re
import datetime
from collections import Counter
from discord.ext import commands, tasks
from discord.ui import Select, View
from discord.ext.commands import Context

from helpers import checks
from helpers.db_manager import add_vote, update_remind_time, delete_expire_event, get_remind_user, voting_record

DEFAULT_TIME_PERIOD = 4
DEFAULT_REMIND_PERIOD = datetime.timedelta(hours=3, minutes=30)
DEFAULT_REMIND_BEFORE_END = datetime.timedelta(minutes=30)
# Here we name the cog and create a new class for the cog.
class Voting(commands.Cog, name="voting"):
    def __init__(self, bot):
        self.bot = bot

        # self.voting : dict{voting_type : dict{'option' : vote_count}} -> maintaining the voting event
        # self.voting_config : dict{voting_type : [min_vote, max_vote, end_time]} -> record the min_vote, max_vote and the time of the end of the vote
        self.voting = dict()
        self.voting_config = dict()

        self.date_pattern = re.compile(r'(\d+)-(\d+)-(\d+)')
        self.time_pattern = re.compile(r'(\d+):(\d+)')


    # Define a hybrid group
    @commands.hybrid_group(
        name="vote",
        description="Voting.",
    )
    @commands.has_permissions(manage_messages=True)
    @checks.not_blacklisted()
    async def vote(self, context: Context) -> None:
        """
        Manage voting of a user on a server.

        :param context: The hybrid command context.
        """
        if context.invoked_subcommand is None:
            embed = discord.Embed(
                description="Please specify a subcommand.\n\n**Subcommands:**\n" + \
                "`add` - Add a vote event.\n" + \
                "`vote` - Make a vote to a specific event.\n" + \
                "`remove` - Remove a vote event.\n" + \
                "`list` - List all vote events.\n" + \
                "`add_option` - Add some options to a vote event.\n" + \
                "`del_option` - Delete some options from a vote event.\n" + \
                "`set_time` - Set the end time of a voting event.\n" + \
                "`end` - Get the end time of a voting event.",
                color=0xE02B2B
            )
            await context.send(embed=embed)

    # define a vote funtion
    @vote.command(
        name="vote",
        description="Vote",
    )
    # This will only allow non-blacklisted members to execute the command
    @checks.not_blacklisted()
    @commands.has_permissions(manage_messages=True)
    async def vote_vote(self, context: Context, voting_type : str=None):
        """
        This is a testing command that does nothing.

        :param context: The application command context.
        """
        # Do your stuff here

        # Don't forget to remove "pass", I added this just because there's no content in the method.
        if voting_type:
            if not self.test_voting_event(voting_type):
                await context.reply(f"Error : The voting type {voting_type} hasn't been created.")
                return

            if len(self.voting[voting_type]) == 0:
                await context.reply(f"Error : There are no options in voting type {voting_type}.")
                return

            select_box = Select(
                min_values=self.voting_config[voting_type][0],
                max_values=self.voting_config[voting_type][1],
                placeholder=f"options for {voting_type}",
                options=[discord.SelectOption(label=f"{option}") for option in list(self.voting[voting_type].keys())])

            async def deal_data(interaction):
                for selected in select_box.values:
                    self.voting[voting_type][selected] += 1
                print(self.voting)
                await interaction.response.send_message(f"You choose : {', '.join(select_box.values)}", ephemeral=True)

            select_box.callback = deal_data
            view = View()
            view.add_item(select_box)
            await context.reply(f"These are the option of {voting_type}.", view=view)
        else:
            pass


    @vote.command(
        name="testing"
    )
    async def vote_testing(self, context: Context):
        channel = self.bot.get_channel(408537090712928260)
        user = self.bot.get_user(408537090712928260)
        await user.send("hello there")
        # print(channel)
        # print(channel.members)
        # channel.send('test msg')

        print(user)


    @vote.command(
        name="add",
        description="Creating a voting event.",
        with_app_command=False
    )
    async def vote_add(self, context: Context, voting_type : str = None, *time : str):
        """
        This is a testing command that does nothing.

        :param context: The application command context.
        """

        try :
            assert(voting_type is not None)
        except :
            await context.reply(f'Error : The voting type should not be None')
            return

        try:
            if len(time) > 3 :
                min_vote = max(int(time[-2]), 1)
                max_vote = max(int(time[-1]), 1)
            else :
                min_vote = 1
                max_vote = max(int(time[-1]), 1)
        except:
            min_vote = 1
            max_vote = 1
        self.voting[voting_type] = dict()
        self.voting_config[voting_type] = [min_vote, max_vote] if min_vote <= max_vote else [max_vote, min_vote]

        # Convert the time into a formal type.
        if time:
            try :
                day = self.date_pattern.findall(time[0])[0]
                time = self.time_pattern.findall(time[1])[0]
                time = [time_val.zfill(2) for time_val in day] + [time_val.zfill(2) for time_val in time]
                print(time)
            except:
                await context.reply(f"Something wrong while setting the time. ValueError : Your input is {', '.join([x for x in time])} The end of the voting period will be set to {DEFAULT_TIME_PERIOD} hours later.")

        if time:
            remind_time = datetime.datetime.now()
            remind_time = remind_time.replace(year=int(f'20{time[0][-2:]}'), month=int(time[1]), day=int(time[2]), hour=int(time[3]), minute=int(time[4]))
            self.voting_config[voting_type].append(f'{remind_time.year}-{remind_time.month}-{remind_time.day} {remind_time.hour}:{remind_time.minute}')
            remind_time -= DEFAULT_REMIND_BEFORE_END
        else:
            remind_time = datetime.datetime.now()
            # default remind time
            remind_time += DEFAULT_REMIND_PERIOD
            end_vote_time = remind_time + DEFAULT_REMIND_BEFORE_END
            self.voting_config[voting_type].append(f'{end_vote_time.year}-{end_vote_time.month}-{end_vote_time.day} {end_vote_time.hour}:{end_vote_time.minute}')
        if remind_time:
            async for user_id in context.guild.fetch_members():
                if not user_id.bot:
                    print(len(await add_vote(server_id=context.guild.id, user_id=user_id, vote_name=voting_type, remind_at=f'{remind_time.year}-{remind_time.month}-{remind_time.day} {remind_time.hour}:{remind_time.minute}')))
        print(self.voting_config[voting_type])
        await context.send(f'Create a voting event : {voting_type} (the event will end at : {self.voting_config[voting_type][-1]})')

    @vote.command(
        name="list",
        description="Showing the existed voting event.",
    )
    async def vote_list(self, context: Context):
        """
        This is a testing command that does nothing.

        :param context: The application command context.
        """

        await context.send(f'Existed voting event : {", ".join([x for x in self.voting.keys()])}')

    @vote.command(
        name="add_option",
        description="Add option to a specific voting.",
        with_app_command=False
    )
    async def vote_add_option(self, context: Context, voting_type: str, *options):
        """
        This is a testing command that does nothing.

        :param context: The application command context.
        """
        print(self.voting.keys())
        if not self.test_voting_event(voting_type):
            await context.reply(f"Error : The voting type {voting_type} hasn't been created.")
            return

        added_option = list()

        for option in options:
            if option not in self.voting[voting_type].keys():
                self.voting[voting_type][option] = 0
                added_option.append(option)

        print(self.voting[voting_type].keys())
        await context.send(f'Added {", ".join([x for x in added_option])} to event {voting_type}')


    @vote.command(
        name="del_option",
        description="Delete option from a specific voting.",
        with_app_command=False
    )
    async def vote_del_option(self, context: Context, voting_type: str, *options):
        """
        This is a testing command that does nothing.

        :param context: The application command context.
        """

        if not self.test_voting_event(voting_type):
            await context.reply(f"Error : The voting type {voting_type} hasn't been created.")
            return

        removed_option = list()
        removed_wrong_option = list()
        removed_failed_option = list()

        for option in options:
            if option in self.voting[voting_type].keys():
                if self.voting[voting_type][option] > 0:
                    removed_failed_option.append(option)
                    continue
                self.voting[voting_type].pop(option)
                removed_option.append(option)
            else:
                removed_wrong_option.append(option)

        print(self.voting[voting_type].keys())

        if removed_option:
            await context.send(f'Deleted {", ".join([x for x in removed_option])} from event {voting_type}')
        if removed_wrong_option:
            await context.reply(f'Option {", ".join([x for x in removed_wrong_option])} are not in voting event {voting_type}')
        if removed_failed_option:
            await context.reply(f"Somebody has voted {', '.join([x for x in removed_failed_option])}. It can't be deleted.")

    @vote.command(
        name="set_time",
        description="Set the end time of a voting event.",
        with_app_command=False
    )
    async def vote_set_time(self, context: Context, voting_type: str, *time : str):

        if not self.test_voting_event(voting_type):
            await context.reply(f"Error : The voting type {voting_type} hasn't been created.")
            return
        # Convert the time into a formal type.
        day = self.date_pattern.findall(time[0])[0]
        time = self.time_pattern.findall(time[1])[0]
        time = [time_val.zfill(2) for time_val in day] + [time_val.zfill(2) for time_val in time]
        print(time)
        if time:
            try:
                remind_time = datetime.datetime.now()
                remind_time = remind_time.replace(year=int(f'20{time[0][-2:]}'), month=int(time[1]), day=int(time[2]), hour=int(time[3]), minute=int(time[4]))
                self.voting_config[voting_type][-1] = f'{remind_time.year}-{remind_time.month}-{remind_time.day} {remind_time.hour}:{remind_time.minute}'
                remind_time -= DEFAULT_REMIND_BEFORE_END
            except:
                await context.reply(f"Something wrong while setting the time. ValueError : Your input is {', '.join([x for x in time])}.")
                return
        print(await update_remind_time(server_id=context.guild.id, vote_name=voting_type, remind_at=f'{remind_time.year}-{remind_time.month}-{remind_time.day} {remind_time.hour}:{remind_time.minute}'))
        await context.reply(f"The end of the time of the voting event {voting_type} has been postponed. The end of the time of the voting event is {int(f'20{time[0][-2:]}')}-{int(time[1])}-{int(time[2])} {int(time[3])}:{int(time[4])}")

    @vote.command(
        name="end",
        description="Get the end time of a voting event.",
    )
    async def vote_end(self, context: Context, voting_type: str):
        if not self.test_voting_event(voting_type):
            await context.reply(f"Error : The voting type {voting_type} hasn't been created.")
            return
        await context.reply(f"The end of the time of the voting event {voting_type} is {self.voting_config[voting_type][-1]}")

    def test_voting_event(self, voting_type: str) -> bool:
        try :
            assert(voting_type in self.voting.keys())
            return True
        except :
            return False

    @commands.Cog.listener()
    async def on_ready(self):
        self.remind.start()
        self.calculate_voting_result.start()

    @tasks.loop(minutes = 1.0)
    async def remind(self):
        remind_time = datetime.datetime.now()
        print(remind_time)
        user_id_list = await get_remind_user(remind_at=f'{remind_time.year}-{remind_time.month}-{remind_time.day} {remind_time.hour}:{remind_time.minute}')
        print(user_id_list)
        for user_id in user_id_list:
            user = self.bot.get_user(user_id)
            await user.send(":poop:")
        await delete_expire_event(remind_at=f'{remind_time.year}-{remind_time.month}-{remind_time.day} {remind_time.hour}:{remind_time.minute}')


    @tasks.loop(minutes = 1.0)
    async def calculate_voting_result(self):
        remind_time = datetime.datetime.now()
        remind_time = f'{remind_time.year}-{remind_time.month}-{remind_time.day} {remind_time.hour}:{remind_time.minute}'
        for voting_event_name, event_config in self.voting_config.items():
            if event_config[-1] == remind_time:
                storing_record = list()
                self.voting_config.pop(voting_event_name)
                voting_record = self.voting.pop(voting_event_name)
                voting_record = Counter(voting_record)
                for k, _ in voting_record.most_common(2):
                    storing_record.append(k)
                if k >= 2:
                    await voting_record(vote_type=voting_event_name, first_place=storing_record[0], second_place=storing_record[1])

# And then we finally add the cog to the bot so that it can load, unload, reload and use it's content.
async def setup(bot):
    await bot.add_cog(Voting(bot))

