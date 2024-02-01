from dotenv import load_dotenv
import os
import discord
from discord.ext import commands
from discord import app_commands
from typing import List

load_dotenv(".env")

TOKEN = os.getenv("TOKEN")
OFFICIAL_SERVER_ID = int(os.getenv("OFFICIAL_SERVER_ID"))
OFFICIAL_CHANNEL_ID = int(os.getenv("OFFICIAL_CHANNEL_ID"))

intents = discord.Intents.all()

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree
guild = None
channel = None
db = {}


async def get_cheat_sheet():
    if (guild is None) or (channel is None):
        print("channel or guild is null")
        return None
    messages = {}
    async for message in channel.history(oldest_first=True):
        title = message.content.split("\n")[0].replace("**", "")
        messages[title] = message.id
    return messages


def create_embed(title: str,
                 data: dict = dict(),
                 inline_default: bool = False,
                 inline_dict: dict() = dict(),
                 description: str = None,
                 footer: str = None,
                 thumbnail: str = None,
                 url: str = None,
                 color: discord.Color = None,
                 black_list: list = []
                 ) -> discord.Embed:
    embed = discord.Embed(title=title, description=description, color=color, url=url)

    for [key, value] in data.items():
        if all([key != i for i in black_list]):
            embed.add_field(name=key + ":", value=value, inline=inline_dict.get(key, inline_default))
    embed.set_footer(text=footer)
    embed.set_thumbnail(url=thumbnail)

    return embed


def text2embed(text: str, color: discord.Color = None) -> discord.Embed:
    title = text.split("\n")[0]
    description = text[len(title):].strip()
    return create_embed(title=title, description=description, color=color)


@tree.command(name="save-cheat-sheet")
async def save(interaction: discord.Interaction):
    allowed_role = discord.utils.get(interaction.guild.roles, name="official editor")

    author = interaction.user
    member = interaction.guild.get_member(author.id)

    if any(role == allowed_role for role in member.roles):
        db['cheat sheet'] = await get_cheat_sheet()

        embed = discord.Embed(title=':white_check_mark: Saved!', description='Cheat Sheet was Saved Successfully', color=discord.Color.green())

        await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        embed = discord.Embed(title=':x: Access Denied.', description=f"You must have the '{allowed_role.mention}' role to use this command.", color=discord.Color.red())
        await interaction.response.send_message(content=" ", ephemeral=True)


@save.error
async def clear_error(interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
    await interaction.response.send_message(content="An error occurred while executing the command.", ephemeral=True)


@tree.command(name="get", description="Get a Piece Code From Our Official Cheat Sheet!")
async def get(interaction: discord.Interaction, code: str):
    channel = discord.utils.get(interaction.guild.channels, name="official-cheat-sheet")
    if channel is None:
        await interaction.response.send_message(content="Invalid channel!", ephemeral=True)
        return

    messages = db['cheat sheet']
    message_id = messages.get(code)

    if message_id is None:
        await interaction.response.send_message(content="Invalid code!", ephemeral=True)
        return

    try:
        message = await channel.fetch_message(message_id)
    except discord.NotFound:
        await interaction.response.send_message(content="Message not found!", ephemeral=True)
        return

    embed = text2embed(message.content)
    if message.attachments:
        embed.set_image(url=message.attachments[0].url)

    await interaction.response.send_message(embed=embed, ephemeral=True)


@get.autocomplete("code")
async def autocomplete_get(interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
    choices = []
    messages = db['cheat sheet']

    for i, message_id in messages.items():
        if current.lower() in i.lower():
            choices.append(app_commands.Choice(name=i, value=i))

    return choices


@tree.command(name='view-code', description='get bot\'s code')
async def view_code(interaction: discord.Interaction):
    embed = create_embed(title="View Bot Code", description='click the button below to view the bot\'s code')
    view = discord.ui.View()
    button = discord.ui.Button(label='repo', style=discord.ButtonStyle.link,
                               url='https://github.com/PhoenixWarriur/magshimim_discord_bot')
    view.add_item(item=button)
    await interaction.response.send_message(embed=embed, view=view)


@bot.event
async def on_message(message):
    if not isinstance(message.channel, discord.TextChannel):
        return

    if message.channel.name != 'official-cheat-sheet':
        return

    if message.author == bot.user:
        return

    db['cheat sheet'][message.content.split("\n")[0].replace("**", "")] = message.id


@bot.event
async def on_ready():
    global guild, channel, db
    await tree.sync()
    print(f"I am {bot.user}")
    guild = bot.get_guild(OFFICIAL_SERVER_ID)
    channel = guild.get_channel(OFFICIAL_CHANNEL_ID)
    db["cheat sheet"] = await get_cheat_sheet()


if __name__ == "__main__":
    bot.run(TOKEN)

