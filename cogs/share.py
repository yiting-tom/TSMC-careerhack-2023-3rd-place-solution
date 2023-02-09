""""
Copyright © Krypton 2019-2023 - https://github.com/kkrypt0nn (https://krypton.ninja)
Description:
🐍 A simple template to start to code your own and personalized discord bot in Python programming language.

Version: 5.5.0
"""

from discord.ext import commands
from discord.ext.commands import Context
from helpers import checks, db_manager
import discord
from discord import ui
from discord import app_commands
from discord.ext.forms import Form, Validator, ReactionForm, ReactionMenu
import math

GUILD_ID = 1070985020841394197


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

        self.tag = select_values[0]

        if self.tag == "新增標籤":
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

        tag = self.children[3].value if self.tag == "新增標籤" else self.tag
        embed = discord.Embed(
            title=f"✅ 成功分享到 #{tag}",
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

        await db_manager.add_share(
            user_id=interaction.user.id,
            server_id=interaction.guild.id,
            title=title,
            description=description,
            url=url,
            tag=tag
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
                `add` - Adds a share\n\n \
                `list` - List shares\n\n \
                `myshares` - Checks your shares\n\n \
                `delete` - Deletes a share\n\n"

            embed = discord.Embed(
                description=description,
                color=0xE02B2B
            )
            await context.send(embed=embed)

    @share.command(
        name="add",
        description="Adds a share",
    )
    @checks.not_blacklisted()
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    async def add(self, context: Context):

        if context.guild is None:
            await context.send("This command can only be used in a server.")
            return

        view = ui.View()
        exist_tags = await db_manager.get_share_tags(server_id=context.guild.id)
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
            ]
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
        description="List shares",
    )
    @checks.not_blacklisted()
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    async def list(self, context: Context):

        if context.guild is None:
            await context.send("This command can only be used in a server.")
            return

        exist_tags = await db_manager.get_share_tags(server_id=context.guild.id)

        if len(exist_tags) == 0:
            await context.send("目前沒有任何分享。")
            return

        options = [
            discord.SelectOption(label=tag, value=tag)
            for tag in exist_tags
        ]

        view = ui.View()
        select_ui = ui.Select(
            placeholder="請選擇標籤",
            options=options
        )

        async def callback(interaction: discord.Interaction):

            await interaction.response.edit_message( content="以下是大家分享的內容" ,embed=None, view=None)

            shares = await db_manager.get_shares_by_tag(
                server_id=context.guild.id,
                tag=select_ui.values[0]
            )

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

                await context.send(embed=embed)

        select_ui.callback = callback
        view.add_item(select_ui)

        await context.send(view=view)

    @share.command(
        name="myshares",
        description="Check your shares!",
    )
    @checks.not_blacklisted()
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    async def check(self, context: Context):

        if context.guild is None:
            await context.send("This command can only be used in a server.")
            return

        # shares is a list of dict, each dict has 4 keys: title, description, url, tag
        shares = await db_manager.check_shares(user_id=context.author.id,
                                               server_id=context.guild.id)

        if len(shares) == 0:
            await context.send("你沒有分享過任何內容。")
            return

        sorted_shares = sorted(shares, key=lambda x: x["tag"])

        embed = discord.Embed(
            title="你分享過的內容",
            color=0x819FF7
        )

        for item in sorted_shares:
            embed.add_field(
                name=f"📄 {item['title']}",
                value=f"標籤: {item['tag']}\n內容: {item['description']}\n連結: {item['url']}",
                inline=False
            )

        await context.send(embed=embed)

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
        shares = await db_manager.check_shares(user_id=context.author.id,
                                               server_id=context.guild.id)

        if len(shares) == 0:
            await context.send("你沒有分享過任何內容。")
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
                await db_manager.delete_shares_by_share_ids(user_id=context.author.id,
                                                            server_id=context.guild.id,
                                                            share_ids=share_ids_to_delete)

                await interaction.message.edit(content="刪除成功", view=None, embed=None)
            elif double_check_ui.value == "no":
                await interaction.message.edit(content="取消刪除", view=None, embed=None)

            double_check_ui.stop()

        select_ui.callback = callback
        view.add_item(select_ui)

        await context.send(view=view)


async def setup(bot):
    await bot.add_cog(Share(bot))
