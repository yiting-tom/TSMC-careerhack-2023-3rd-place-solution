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
from helpers.db_manager import add_vote, update_remind_time, delete_expire_event, get_remind_user, vote_record, delete_vote_user

DEFAULT_TIME_PERIOD = 4
DEFAULT_REMIND_PERIOD = datetime.timedelta(hours=3, minutes=30)
DEFAULT_REMIND_BEFORE_END = datetime.timedelta(minutes=30)
# Here we name the cog and create a new class for the cog.
class Voting(commands.Cog, name="voting"):
    def __init__(self, bot):
        self.bot = bot

        # self.voting : dict{voting_type : dict{'user_id' : [options]}} -> maintaining the voting event -> It is better to store the event in the database for resuming the event
        # self.voting_option : dict{voting_type : [options]} -> maintaining the voting event's option -> It is better to store the event in the database for resuming the event
        # self.voting_config : dict{voting_type : [min_vote, max_vote, end_time]} -> record the min_vote, max_vote and the time of the end of the vote
        self.voting = dict()
        self.voting_option = dict()
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
        # Don't forget to remove "pass", I added this just because there's no content in the method.
        if not self.test_voting_event(voting_type):
            await context.reply(f"Error : The voting type {voting_type} hasn't been created.", ephemeral=True)
            return

        if len(self.voting_option[voting_type]) == 0:
            await context.reply(f"Error : There are no options in voting type {voting_type}.", ephemeral=True)
            return

        select_box = Select(
            min_values=self.voting_config[voting_type][0],
            max_values=self.voting_config[voting_type][1],
            placeholder=f"options for {voting_type}",
            options=[discord.SelectOption(label=f"{option}") for option in self.voting_option[voting_type]])

        async def deal_data(interaction):
            self.voting[voting_type][str(interaction.user.id)] = list(select_box.values)
            print(self.voting)
            await interaction.response.send_message(f"You choose : {', '.join(select_box.values)}", ephemeral=True)
            await delete_vote_user(server_id=interaction.guild_id, user_id=interaction.user.id, vote_name=voting_type)
        select_box.callback = deal_data
        view = View()
        view.add_item(select_box)

        counted_votes = Counter()
        for personal_vote in self.voting[voting_type].values():
            counted_votes += Counter(personal_vote)
        embed = discord.Embed(
            description=f"The number of votes of each option :\n{', '.join([f'{k} : {v}'for k, v in counted_votes.items()])}",
            color=0xE02B2B
        )
        await context.reply(f"These are the option of {voting_type}.", embed=embed, view=view)

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
            await context.reply(f'Error : The voting type should not be None', ephemeral=True)
            return

        min_vote = 1
        max_vote = 1
        self.voting[voting_type] = dict()
        self.voting_option[voting_type] = list()
        self.voting_config[voting_type] = [min_vote, max_vote] if min_vote <= max_vote else [max_vote, min_vote]

        # Convert the time into a formal type.
        if time:
            try :
                day = self.date_pattern.findall(time[0])[0]
                time = self.time_pattern.findall(time[1])[0]
                time = [time_val.zfill(2) for time_val in day] + [time_val.zfill(2) for time_val in time]
                print(time)
            except:
                await context.reply(f"Something wrong while setting the time. ValueError : Your input is {', '.join([x for x in time])} The end of the voting period will be set to {DEFAULT_TIME_PERIOD} hours later.", ephemeral=True)

        if time:
            remind_time = datetime.datetime.now()
            remind_time = remind_time.replace(year=int(f'20{time[0][-2:]}'), month=int(time[1]), day=int(time[2]), hour=int(time[3]), minute=int(time[4]))
            self.voting_config[voting_type].append(f'{remind_time.year}-{str(remind_time.month).zfill(2)}-{str(remind_time.day).zfill(2)} {str(remind_time.hour).zfill(2)}:{str(remind_time.minute).zfill(2)}')
            remind_time -= DEFAULT_REMIND_BEFORE_END
        else:
            remind_time = datetime.datetime.now()
            # default remind time
            remind_time += DEFAULT_REMIND_PERIOD
            end_vote_time = remind_time + DEFAULT_REMIND_BEFORE_END
            self.voting_config[voting_type].append(f'{end_vote_time.year}-{str(end_vote_time.month).zfill(2)}-{str(end_vote_time.day).zfill(2)} {str(end_vote_time.hour).zfill(2)}:{str(end_vote_time.minute).zfill(2)}')
        if remind_time:
            print(context.channel.members)
            for user_id in context.channel.members:
                if not user_id.bot:
                    print(len(await add_vote(server_id=context.guild.id, user_id=user_id, vote_name=voting_type, remind_at=f'{remind_time.year}-{str(remind_time.month).zfill(2)}-{str(remind_time.day).zfill(2)} {str(remind_time.hour).zfill(2)}:{str(remind_time.minute).zfill(2)}')))
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

        await context.send(f'Existed voting event : {", ".join([x for x in self.voting_option.keys()])}', ephemeral=True)

    @vote.command(
        name="max_vote",
        description="Showing the existed voting event.",
    )
    async def vote_max_vote(self, context: Context, voting_type : str, max_vote : int):
        """
        This is a testing command that does nothing.

        :param context: The application command context.
        """
        try :
            assert(voting_type is not None)
        except :
            await context.reply(f'Error : The voting type should not be None', ephemeral=True)
            return

        try :
            assert(self.voting_option.get(voting_type, None) is not None)
        except :
            await context.reply(f"Error : The voting type hasn't been created.", ephemeral=True)
            return
        if max_vote > self.voting_config[voting_type][0] :
            self.voting_config[voting_type][1] = max_vote
            await context.send(f"The voting event {voting_type}'s max_vote is set to {max_vote}.")
        else :
            await context.send(f"ValueError : {max_vote} is not a valid number.", ephemeral=True)
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
            await context.reply(f"Error : The voting type {voting_type} hasn't been created.", ephemeral=True)
            return

        added_option = list()

        for option in options:
            if option not in self.voting_option[voting_type]:
                self.voting[voting_type] = dict()
                added_option.append(option)
                self.voting_option[voting_type].append(option)

        print(self.voting_option[voting_type])
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
            await context.reply(f"Error : The voting type {voting_type} hasn't been created.", ephemeral=True)
            return

        removed_option = list()
        removed_wrong_option = list()
        removed_failed_option = list()

        print(options)
        for option in options:
            fail_flag = False
            for personal_vote in self.voting[voting_type].values():
                if option in personal_vote:                       
                    removed_failed_option.append(option)
                    fail_flag = True
                    continue
            if option not in self.voting_option[voting_type]:
                removed_wrong_option.append(option)
                continue
            elif fail_flag:
                continue
            self.voting_option[voting_type].pop(self.voting_option[voting_type].index(option))
            removed_option.append(option)

        print(self.voting_option[voting_type])

        if removed_option:
            await context.send(f'Deleted {", ".join([x for x in removed_option])} from event {voting_type}')
        if removed_wrong_option:
            await context.reply(f'Option {", ".join([x for x in removed_wrong_option])} are not in voting event {voting_type}', ephemeral=True)
        if removed_failed_option:
            await context.reply(f"Somebody has voted {', '.join([x for x in removed_failed_option])}. It can't be deleted.", ephemeral=True)

    @vote.command(
        name="set_time",
        description="Set the end time of a voting event.",
        with_app_command=False
    )
    async def vote_set_time(self, context: Context, voting_type: str, *time : str):

        if not self.test_voting_event(voting_type):
            await context.reply(f"Error : The voting type {voting_type} hasn't been created.", ephemeral=True)
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
                self.voting_config[voting_type][-1] = f'{remind_time.year}-{str(remind_time.month).zfill(2)}-{str(remind_time.day).zfill(2)} {str(remind_time.hour).zfill(2)}:{str(remind_time.minute).zfill(2)}'
                remind_time -= DEFAULT_REMIND_BEFORE_END
            except:
                await context.reply(f"Something wrong while setting the time. ValueError : Your input is {', '.join([x for x in time])}.", ephemeral=True)
                return
        print(await update_remind_time(server_id=context.guild.id, vote_name=voting_type, remind_at=f'{remind_time.year}-{str(remind_time.month).zfill(2)}-{str(remind_time.day).zfill(2)} {str(remind_time.hour).zfill(2)}:{str(remind_time.minute).zfill(2)}'))
        await context.reply(f"The end of the time of the voting event is set to {int(f'20{time[0][-2:]}')}-{int(time[1])}-{int(time[2])} {int(time[3])}:{int(time[4])}")

    @vote.command(
        name="end",
        description="Get the end time of a voting event.",
    )
    async def vote_end(self, context: Context, voting_type: str):
        if not self.test_voting_event(voting_type):
            await context.reply(f"Error : The voting type {voting_type} hasn't been created.", ephemeral=True)
            return
        await context.reply(f"The end of the time of the voting event {voting_type} is {self.voting_config[voting_type][-1]}")

    def test_voting_event(self, voting_type: str) -> bool:
        try :
            assert(voting_type in self.voting_option.keys())
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
        user_event_list = await get_remind_user(remind_at=f'{remind_time.year}-{str(remind_time.month).zfill(2)}-{str(remind_time.day).zfill(2)} {str(remind_time.hour).zfill(2)}:{str(remind_time.minute).zfill(2)}')
        print(user_event_list)
        for user_event in user_event_list:
            user = self.bot.get_user(user_event[0])
            guild_name = self.bot.get_guild(int(user_event[2])).name
            await user.send(f"You have a voting event {user_event[1]} in server {guild_name}")
        await delete_expire_event(remind_at=f'{remind_time.year}-{str(remind_time.month).zfill(2)}-{str(remind_time.day).zfill(2)} {str(remind_time.hour).zfill(2)}:{str(remind_time.minute).zfill(2)}')


    @tasks.loop(minutes = 1.0)
    async def calculate_voting_result(self):
        remind_time = datetime.datetime.now()
        remind_time = f'{remind_time.year}-{str(remind_time.month).zfill(2)}-{str(remind_time.day).zfill(2)} {str(remind_time.hour).zfill(2)}:{str(remind_time.minute).zfill(2)}'
        for voting_event_name, event_config in self.voting_config.items():
            if event_config[-1] == remind_time:
                storing_record = list()
                self.voting_config.pop(voting_event_name)
                self.voted_id.pop(voting_event_name)
                voting_record = self.voting.pop(voting_event_name)
                voting_record = Counter(voting_record)
                for k, _ in voting_record.most_common(2):
                    storing_record.append(k)
                if k >= 2:
                    await vote_record(vote_type=voting_event_name, first_place=storing_record[0], second_place=storing_record[1])

# And then we finally add the cog to the bot so that it can load, unload, reload and use it's content.
async def setup(bot):
    await bot.add_cog(Voting(bot))

