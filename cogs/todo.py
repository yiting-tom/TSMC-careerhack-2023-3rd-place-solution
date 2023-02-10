""""
Copyright © Krypton 2019-2023 - https://github.com/kkrypt0nn (https://krypton.ninja)
Description:
🐍 A simple template to start to code your own and personalized discord bot in Python programming language.

Version: 5.5.0
"""

import asyncio
import random
import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Context
from helpers import checks, db_manager
from discord.ext.forms import Form, Validator, ReactionForm, ReactionMenu
import adapters.todo as todo_adapter
from discord import ui
import random


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


golden_words = [
    "想改變命運，首先要改變自己。",
    "今天的成功是因為昨天的積累，明天的成功則依賴於今天的努力。成功需要一個過程。",
    "命運掌握在自己手裡，命運的好壞由自己去創造。",
    "如果我們投一輩子石塊，即使閉著眼睛，也肯定有一次擊中成功。",
    "好好的管教你自己，不要管別人。",
    "先把魚網打開，魚兒才能找到漁網的入口。",
    "不幸往往來自比較，而幸福也是來自比較。",
    "風暴再大，它終不能刮到你的內心去。",
    "不寬恕眾生，不原諒眾生，是苦了你自己。",
    "阻止你前行的，不是人生道路上的一百塊石頭，而是你鞋子裡的那一顆石子。",
    "積木搭起的房子看似很美，卻會在不經意間轟然倒塌。",
    "當你握著兩手沙子時，一定就拿不到地上那顆珍珠了。",
    "每一種創傷，都是一種成熟。",
    "用鞭子抽著，陀螺才會鏇轉。",
    "成功需要付出代價，不成功需要付出更高的代價。",
    "寧可失敗在你喜歡的事情上，也不要成功在你所憎惡的事情上。",
    "生活本沒有導演，但我們每個人都像演員一樣，為了合乎劇情而認真地表演著。",
    "不管別人臉上有沒有飯粒，都請你先照照鏡子。",
    "相信信念能夠戰勝一切，這本身就是一個最偉大的信念。",
    "再長的路，一步步也能走完，再短的路，不邁開雙腳也無法到達。",
    "長在我們大腦左右的耳朵，往往左右我們的大腦。",
    "成功不是將來才有的，而是從決定去做的那一刻起，持續累積而成。",
    "一個細節足以改變一生。",
    "得不到的東西永遠總是最好的，失去的戀情總是讓人難忘的，失去的人永遠是刻骨銘心的。",
    "有無目標是成功者與平庸者的根本差別。",
    "給事物賦予什麼樣的價值，人們就有什麼樣的行動。",
    "把困難舉在頭上，它就是滅頂石；把困難踩在腳下，它就是墊腳石。",
    "起跑領先一小步，人生領先一大步。",
    "設立目標，然後把目標細化為每一步的實際行動。", "時間才是每個人的終極資源。", "既然一切都會過去，那我們一定要抓住現在的。", "阻礙我們飛翔的力量，是來自我們內心的恐懼。", "本性的甦醒，往往在遭遇真實之後。", "才能一旦讓懶惰支配，它就一無可為。", "相信朋友的忠誠。相信自己的勇氣。相信敵人的愚蠢。", "生氣是拿別人做錯的事來懲罰自己。", "快樂是一種能力。", "如果不想被打倒，只有增加自身的重量。", "自卑是更可怕的貧窮。", "最堅固的捆綁是習慣。", "如果可以重新活一次，每個人都將是成功者。", "除了自己，任何人都無法給你力量。", "時間給勤勉的人留下智慧的力量，給懶惰的人留下空虛和悔恨。", "勤學的人，總是感到時間過得太快；懶惰的人，卻總是埋怨時間跑得太慢。", "每個人都有潛在的能量，只是很容易：被習慣所掩蓋，被時間所迷離，被惰性所消磨。", "在比夜更深的地方，一定有比夜更黑的眼睛。", "人生就像一個大舞台，每個人都有自己所要扮演的角色。至於要表演甚么角色，自己去決定。", "如果你很聰明，為什麼不富有呢？", "只有傻瓜才用雙腳去試河水的深淺。", "炫耀是需要觀眾的，而炫耀恰恰讓我們失去觀眾。",  "如果敵人讓你生氣，那說明你還沒有勝他的把握。", "理論是一碼事，實際又是一碼事。", "知識玩轉財富。", "有人在光明中注視著陰影，有人在陰影中眺望著光明。", "解決最複雜的事情往往需要最簡單的方法。", "時光就像一輛畜力車，它的速度取決於我們手中的鞭子。", "快樂不是因為擁有的多，而是因為計較的少。", "時間是個常數，但也是個變數。勤奮的人無窮多，懶惰的人無窮少。", "沒有退路的時候，正是潛力發揮最大的時候。", "思路決定出路，氣度決定高度，細節決定成敗，性格決定命運。", "沒有糟糕的事情，只有糟糕的心情。", "我們總在關注我們得到的東西是否值錢，而往往忽略放棄的東西是否可惜。", "沒有什麼比順其自然更有超凡的力量。沒有什麼比順乎本性更具有迷人的魔力。", "心有多大，世界就有多大！", "最熱烈的火焰，冰封在最沉默的火山深處。", "漫無目的的生活就像出海航行而沒有指南針。", "當偉人真正站在你面前，你會覺得他比你矮。", "因害怕失敗而不敢放手一搏，永遠不會成功。", "不如意的時候不要盡往悲傷里鑽，想想有笑聲的日子吧。", "我們不行，往往不是因為我們不行，而是因為別人說了我們不行。", "當你看到一個沒有右手的人，就不會抱怨你右手上的哪個胎記了。", "能使我們感覺快樂的，不是環境，而是態度。", "所謂英雄，其實是指那些無論在什麼環境下都能夠生存下去的人。", "懶惰是意志薄弱者的隱藏所。", "人的活動如果沒有理想的鼓舞，就會變得空虛而渺小。", "告訴你一個寶藏的地點，它就在你的生命里。", "懶惰受到的懲罰不僅僅是自己的失敗，還有別人的成功。", "時間是最公開合理的，它從不多給誰一份，勤勞者能叫時間留給串串的果實，懶惰者時間給予他們一頭白髮，兩手空空。", "不論你在什麼時候開始，重要的是開始之後就不要停止；不論你在什麼時候結束，重要的是結束之後就不要悔恨。", "所有的勝利，與征服自己的勝利比起來，都是微不足道；所有的失敗，與失去自己的失敗比起來，更是微不足道。", "只要站起來比倒下去多一次就是成功。",    "如果敵人讓你生氣，那說明你還沒有勝他的把握。", "如果你堅信自己最優秀，那么你就最聰明。", "後悔是一種耗費精神的情緒，後悔是比損失更大的損失，比錯誤更大的錯誤，所以不要後悔。", "失敗緣於忽視細處，成功始於重視小事。", "人生的冷暖取決於心靈的溫度。", "人最可悲的是自己不能戰勝自己。", "勤奮可以彌補聰明的不足，但聰明無法彌補懶惰的缺陷。", "狂妄的人有救，自卑的人沒有救。", "荊棘的存在是為了野草不輕易地任人踐踏。", "聰明人創造的機會多於碰到的機會。", "只有舍，才有得。", "只要努力，你就能成為你想成為的人。", "勤奮和智慧是雙胞胎，懶惰和愚蠢是親兄弟。", "你用一百分的努力和成功做交換，沒有不成交的。", "千萬人的失敗，都有是失敗在做事不徹底，往往做到離成功只差一步就終止不做了。", "信念是一把無堅不摧的利刃。", "爬上最高的境界，你會陡然發現：那裡的景色竟然是你司空見慣的。", "目光能看多遠，你就能走多遠。", "改變自我，挑戰自我，從現在開始。", "一切皆有因果。", "「真正的成就，不在於做。了一件偉大的事，而是累積每天的平凡。」——王品集團董事長戴勝"
]


def create_embed_by_todo_list(todo_list, title: str = "To-do list"):
    embed = discord.Embed(
        title=f"{title}" if len(todo_list) > 0 else "To-do list is empty",
        color=0x8AB6F1
    )

    for todo in todo_list:
        embed.add_field(
            name=f"📝\t{todo['subject']}",
            value=todo["description"],
            inline=False
        )

    return embed


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

        form = Form(context, '新增內容到 To-Do List', cleanup=False)
        form.add_question("請輸入待辦工作內容", "subject", to_str)
        form.add_question("請輸入備註", "description", to_str)

        result = await form.start()

        todo_adapter.add_todo(
            user_id=context.author.id,
            subject=result.subject,
            description=result.description,
        )

        embed = discord.Embed(
            title="成功新增事項到 To-Do List ✅",
            color=0xE02B2B
        )

        embed.add_field(name="待辦工作內容", value=result.subject, inline=False)
        embed.add_field(
            name="備註", value=result.description, inline=False)

        await context.send(embed=embed)

    @todo.command(
        name="list",
        description="檢視 To-Do List",
    )
    @checks.not_blacklisted()
    async def todo_list(self, context: Context):

        todos = todo_adapter.get_todos(user_id=context.author.id)

        embed = create_embed_by_todo_list(
            todos, title=f"嗨 {context.author.name}，以下是你的 To-Do List")

        await context.send(embed=embed, ephemeral=True)

    @todo.command(
        name="complete",
        description="完成事項",
    )
    @checks.not_blacklisted()
    async def todo_complete(self, context: Context):
        """Let user select what to delete."""

        todos = todo_adapter.get_todos(user_id=context.author.id)

        view = ui.View()
        select_todo_ui = ui.Select(
            placeholder="請選擇已完成的事項",
            options=[
                discord.SelectOption(
                    label=f"{todo['subject']}",
                    value=f"{todo['todo_id']}",
                    description=f"{todo['description']}",
                )
                for todo in todos
            ],
            min_values=1,
            max_values=max(len(todos), 1),
        )

        async def callback(interaction: discord.Interaction):

            todo_ids_to_delete = [int(todo_id)
                                  for todo_id in select_todo_ui.values]

            double_check_ui = ButtonCheck()
            await interaction.response.edit_message(content=f"確認已完成?", view=double_check_ui)
            await double_check_ui.wait()

            if double_check_ui.value == "yes":
                todo_adapter.delete_todo_by_ids(
                    todo_ids=todo_ids_to_delete)

                todo_remain_embed = create_embed_by_todo_list(
                    todo_adapter.get_todos(user_id=context.author.id),
                    title=f"嗨 {context.author.name}，以下是你的 To-Do List",
                )
                await interaction.message.edit(content="事項已完成👏", view=None, embed=todo_remain_embed)
            elif double_check_ui.value == "no":
                await interaction.message.edit(content="取消", view=None, embed=todo_remain_embed)

        select_todo_ui.callback = callback
        view.add_item(select_todo_ui)

        await context.send(view=view)

# And then we finally add the cog to the bot so that it can load, unload, reload and use it's content.


async def setup(bot):
    await bot.add_cog(Todo(bot))
