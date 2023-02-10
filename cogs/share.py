""""
Copyright © Krypton 2019-2023 - https://github.com/kkrypt0nn (https://krypton.ninja)
Description:
🐍 A simple template to start to code your own and personalized discord bot in Python programming language.

Version: 5.5.0
"""

from typing import List
from discord.ext import commands
from discord.ext.commands import Context
from helpers import checks
import discord
from discord import ui
from discord import app_commands
from discord.ext.forms import Form, Validator, ReactionForm, ReactionMenu
import math
import models.share as share_model
import adapters.share as share_adapter
from utils.logger import L

GUILD_ID = 1070985020841394197


def expan_tags(tags: List[str]):
    """Expand tags

    Args:
        tags (list): list of tags

    Returns:
        str: expanded tags
    """
    return ", ".join([f"`{t}`" for t in tags])


class ButtonCheck(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None

    @discord.ui.button(label="✅", style=discord.ButtonStyle.secondary)
    async def confirm(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.value = "yes"
        self.stop()

    @discord.ui.button(label="❌", style=discord.ButtonStyle.secondary)
    async def cancel(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.value = "no"
        self.stop()


class ShareAddModal(ui.Modal):
    def __init__(self, title="新增分享", select_values="新增標籤", **kwargs):

        super().__init__(title=title)

        self.add_item(ui.TextInput(
            label="Title",
            required=True,
            max_length=255
        ))
        self.add_item(ui.TextInput(
            label="Description",
            required=True,
            style=discord.TextStyle.paragraph,
            max_length=255
        ))
        self.add_item(ui.TextInput(
            label="Url",
            max_length=255
        ))

        self.tags = select_values  # list of tags(str)

        if "新增標籤" in self.tags:
            self.add_item(ui.TextInput(
                label="Tag",
                placeholder="請輸入標籤",
                min_length=1,
                max_length=50
            ))

    async def on_submit(self, interaction: discord.Interaction):

        title = self.children[0].value
        description = self.children[1].value
        url = self.children[2].value

        if "新增標籤" in self.tags:
            self.tags.append(self.children[3].value)  # add new tag to list
            self.tags.remove("新增標籤")

        embed = discord.Embed(
            title=f"✅ 成功分享",
            color=0x819FF7,
        )

        embed.set_author(
            name=interaction.user.name,
            icon_url=interaction.user.avatar.url if interaction.user.avatar else interaction.user.default_avatar.url,
        )
        embed.add_field(
            name="Title", value=title, inline=False)

        embed.add_field(name="Description",
                        value=description, inline=False)
        embed.add_field(
            name="Url", value=url, inline=False)

        embed.add_field(
            name="Tags", value=expan_tags(self.tags), inline=False)

        share_adapter.add_share(
            user_id=interaction.user.id,
            server_id=interaction.guild.id,
            title=title,
            description=description,
            url=url,
            tags=self.tags
        )

        await interaction.response.edit_message(embed=embed, view=None)


class Share(commands.Cog, name="share", description="Share your content!"):
    """https://github.com/thrzl/discord-ext-forms

    Args:
        commands (_type_): _description_
        name (str, o ptional): _description_. Defaults to "form".
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_group(
        name="share",
        description="Share your content!",
    )
    @checks.not_blacklisted()
    async def share(self, context: Context):
        if context.invoked_subcommand is None:

            description =  \
                "Please specify a subcommand.\n\n \
                ** Subcommands **\n\n \
                `add` - 新增分享\n\n \
                `list` - 列出分享清單\n\n \
                `myshares` - 查看你分享過的內容\n\n \
                `delete` - 刪除你分享過的內容\n\n"

            embed = discord.Embed(
                description=description,
                color=0xE02B2B
            )
            await context.send(embed=embed)

    @share.command(
        name="add",
        description="新增分享",
    )
    @checks.not_blacklisted()
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    async def add(self, context: Context):

        if context.guild is None:
            await context.send("This command can only be used in a server.")
            return

        view = ui.View()
        exist_tags = share_adapter.get_share_tags_by_server_id(
            server_id=context.guild.id)
        options_dict = {
            "新增標籤": "新增標籤",
        }
        for tag in exist_tags:
            options_dict[tag] = tag

        select_ui = ui.Select(
            placeholder="請選擇或是新增標籤",
            options=[
                discord.SelectOption(label=label, value=value)
                for label, value in options_dict.items()
            ],
            min_values=1,
            max_values=max(len(exist_tags), 1),
        )

        async def callback(interaction: discord.Interaction):
            modal = ShareAddModal(title="新增分享", select_values=select_ui.values)
            await interaction.response.send_modal(modal)

        select_ui.callback = callback
        view.add_item(select_ui)

        await context.send(view=view)

        # remove users message
        await context.message.delete()

    @share.command(
        name="list",
        description="列出分享清單",
    )
    @checks.not_blacklisted()
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    async def list(self, context: Context, query: str = None):

        if context.guild is None:
            await context.send("This command can only be used in a server.", ephemeral=True)
            return

        exist_tags = share_adapter.get_share_tags_by_server_id(
            server_id=context.guild.id)

        if len(exist_tags) == 0:
            await context.send("目前沒有任何分享。", ephemeral=True)
            return

        options = [
            discord.SelectOption(label=tag, value=tag)
            for tag in exist_tags
        ]

        view = ui.View()
        select_ui = ui.Select(
            placeholder="請選擇標籤",
            options=options,
            min_values=1,
            max_values=max(1, len(options)),
        )

        async def callback(interaction: discord.Interaction):

            await interaction.response.edit_message(content="以下是大家分享的內容", embed=None, view=None)

            shares = share_adapter.get_shares_by_tags(
                tags=select_ui.values,
            )

            shares = [s for s in shares if s["server"]
                      == str(context.guild.id)]

            if query is not None:
                shares = [s for s in shares if query in s["title"]
                          or query in s["description"]]

            embed_per_page = 5

            if len(shares) > embed_per_page:

                embed_list = []

                for i in range(0, len(shares), embed_per_page):

                    embed = discord.Embed(
                        title=f"({int(i/embed_per_page+1)}/{math.ceil(len(shares)/embed_per_page)}) Posts of #{select_ui.values[0]}",
                        color=0x819FF7,
                    )

                    for share in shares[i:i+embed_per_page]:
                        embed.add_field(
                            name=f"📄 {share['title']}",
                            value=f"{share['description']}\n{share['url']}\n",
                            inline=False
                        )

                    embed_list.append(embed)

                form = ReactionMenu(context, embed_list)
                await form.start()
            else:

                embed = discord.Embed(
                    title=f"Shares of #{select_ui.values[0]}",
                    color=0x819FF7,
                )

                for share in shares:
                    embed.add_field(
                        name=f"📄 {share['title']}",
                        value=f"{share['description']}\n{share['url']}\n",
                        inline=False
                    )

                await context.send(embed=embed, ephemeral=True)

        select_ui.callback = callback
        view.add_item(select_ui)

        await context.send(view=view, ephemeral=True)

    @share.command(
        name="myshares",
        description="查看你分享過的內容",
    )
    @checks.not_blacklisted()
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    async def check(self, context: Context):

        if context.guild is None:
            await context.send("This command can only be used in a server.")
            return

        # shares is a list of dict, each dict has 4 keys: title, description, url, tag
        shares = share_adapter.get_shares_by(
            column="user", keys=[str(context.author.id)])

        shares = [s for s in shares if s["server"] == str(context.guild.id)]

        if len(shares) == 0:
            await context.send("你沒有分享過任何內容。", ephemeral=True)
            return

        sorted_shares = sorted(shares, key=lambda x: x["share_id"])

        embed = discord.Embed(
            title="你分享過的內容",
            color=0x819FF7
        )

        for item in sorted_shares:

            item_tags = []
            for t in item["tags"]:
                item_tags.append(t["tag_tag_id"])

            embed.add_field(
                name=f"📄 {item['title']}",
                value=f"標籤: {expan_tags(item_tags)}\n內容: {item['description']}\n連結: {item['url']}",
                inline=False
            )

        await context.send(embed=embed, ephemeral=True)

    @share.command(
        name="delete",
        description="刪除你分享過的內容",
    )
    @checks.not_blacklisted()
    async def delete(self, context: Context):

        if context.guild is None:
            await context.send("This command can only be used in a server.")
            return

        # shares is a list of dict, each dict has 4 keys: title, description, url, tag
        shares = share_adapter.get_shares_by(
            column="user", keys=[str(context.author.id)])

        shares = [s for s in shares if s["server"] == str(context.guild.id)]

        if len(shares) == 0:
            await context.send("你沒有分享過任何內容。", ephemeral=True)
            return

        options = [
            discord.SelectOption(label="取消", value="cancel")
        ]

        options.extend([
            discord.SelectOption(
                label=share["title"],
                value=share["share_id"],
                description=share['description'][:30]
            )
            for share in shares
        ])

        view = ui.View()
        select_ui = ui.Select(
            placeholder="請選擇要刪除的分享",
            options=options,
            min_values=1,
            max_values=max(len(options), 1)
        )

        async def callback(interaction: discord.Interaction):

            share_ids_to_delete = select_ui.values

            if "cancel" in share_ids_to_delete:
                await interaction.message.edit(content="取消刪除", view=None)
                return

            double_check_ui = ButtonCheck()

            await interaction.response.edit_message(content=f"確認刪除?", view=double_check_ui)
            await double_check_ui.wait()

            if double_check_ui.value == "yes":
                share_adapter.delete_shares_by_share_ids(
                    share_ids=share_ids_to_delete)

                await interaction.message.edit(content="刪除成功", view=None, embed=None)
            elif double_check_ui.value == "no":
                await interaction.message.edit(content="取消刪除", view=None, embed=None)

            double_check_ui.stop()

        select_ui.callback = callback
        view.add_item(select_ui)

        await context.send(view=view, ephemeral=True)


async def setup(bot):
    await bot.add_cog(Share(bot))
