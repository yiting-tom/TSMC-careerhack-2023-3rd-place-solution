""""
Copyright © Krypton 2019-2023 - https://github.com/kkrypt0nn (https://krypton.ninja)
Description:
🐍 A simple template to start to code your own and personalized discord bot in Python programming language.
Version: 5.5.0
"""
import os
import requests

import discord
from discord.ext import commands
from discord.ext.commands import Context
from dotenv import load_dotenv

from helpers import checks

load_dotenv()
OPENAI_ENABLED = True if os.getenv("OPENAI_ENABLED") in ["True", "true", "1"] else False
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MAX_TOKENS = os.getenv("OPENAI_MAX_TOKENS")

# Here we name the cog and create a new class for the cog.
class Chat(commands.Cog, name="chat"):
    def __init__(self, bot):
        self.bot = bot

    # Here you can just add your own commands, you'll always need to provide "self" as first parameter.

    @commands.hybrid_command(
        name="chat",
        description="This is an API to ChatGPT.",
    )
    # This will only allow non-blacklisted members to execute the command
    @checks.not_blacklisted()
    # This will only allow owners of the bot to execute the command -> config.json
    # @checks.is_owner()
    async def chatcommand(self, context: Context):
        # check if openai api is enabled
        if not OPENAI_ENABLED:
            embed = discord.Embed(
                description="You haven't enabled OpenAI API. Please contact the bot owner.",
                color=0xE02B2B
            )
            await context.send(embed=embed)

        # check if user has provided a prompt
        prompt = context.message.content[len(context.prefix + "chat "):]

        if prompt == "":
            embed = discord.Embed(
                description="Please type the message you want to chat with the ChatGPT 🤖.",
                color=0xE02B2B
            )
            await context.send(embed=embed)

        # construct prompt for openai api
        prompt = context.message.content[len(context.prefix + "chat "):]
        prompt = f"I'm {context.message.author.name}: " + prompt

        # request to openai api
        response = requests.post(
            url='https://api.openai.com/v1/completions',
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {OPENAI_API_KEY}'
            },
            json = {
                'model': 'text-davinci-003',
                'prompt': prompt,
                'temperature': 0.4,
                'max_tokens': 300
            }
        )

        # resoponse with error
        if response.status_code != 200:
            embed = discord.Embed(
                description=response.json()['error']['message'],
                color=0xE02B2B
            )
            await context.send(embed=embed)
        
        await context.reply(f"**ChatGPT 🤖 say:** {response.json()['choices'][0]['text']}")
        

# And then we finally add the cog to the bot so that it can load, unload, reload and use it's content.
async def setup(bot):
    await bot.add_cog(Chat(bot))