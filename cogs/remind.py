""""
Copyright © Krypton 2019-2023 - https://github.com/kkrypt0nn (https://krypton.ninja)
Description:
🐍 A simple template to start to code your own and personalized discord bot in Python programming language.

Version: 5.5.0
"""

import discord
from discord.ext import commands
from discord.ext.commands import Context

from helpers import checks


# Here we name the cog and create a new class for the cog.
class Remind(commands.Cog, name="remind"):
    def __init__(self, bot):
        self.bot = bot

        # self.voting : dict{voting_type : dict{'option' : vote_count}} -> maintaining the voting event
        # self.voting_config : dict{voting_type : [min_vote, max_vote, end_time]} -> record the min_vote, max_vote and the time of the end of the vote
        self.voting = dict()
        self.voting_config = dict()

    # Here you can just add your own commands, you'll always need to provide "self" as first parameter.

    @commands.hybrid_group(
        name="remind",
        description="Remind.",
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
                "`add` - Add a remind event.\n" + \
                "`remove` - Remove a vote event.\n" + \
                "`list` - List all vote events.\n" + \
                "`set_time` - Set the end time of a voting event.\n",
                color=0xE02B2B
            )
            await context.send(embed=embed)

    

# And then we finally add the cog to the bot so that it can load, unload, reload and use it's content.
async def setup(bot):
    await bot.add_cog(Remind(bot))
