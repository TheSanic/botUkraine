# coding=utf-8
import discord
from discord.ext import commands
from discord import Embed
from os import environ
import asyncio
from random import randrange

# Переменные(Variables)

byte_array = bytearray([0xFE, 0x01])
client_token = environ.get('client_token', None)
Client = discord.Client()
bot_prefix = "!"
client = commands.Bot(command_prefix=bot_prefix)
help_menu = ("```Так здраствет Україна!\n\nСписок команд:\n!remove [2-100] - Удалить данное количество сообщений\n" 
            "!online - Показать онлайн сервера\n!choice [1, 2, ..] - Выбрать между несколькими элементами\n"
            "!help - Вывести это сообщение```")

# Главная часть(main)

@client.event
async def on_ready():
    print("-----------[Оповещение]-----------\nБот был успешно запущен!\nПоключен как:\nИмя: {0}\n"
          "ID: {1}\n----------------------------------".format(client.user.name, client.user.id))
    await client.change_presence(
        game=discord.Game(name="!help - помощь по командам", url="https://www.twitch.tv/twitch", type=1))


@client.event
async def on_member_join(member):
    role = discord.utils.find(lambda r: r.name == "Player", member.server.roles)
    await client.replace_roles(member, role)


async def choice(message, choices):
    choicesArr = choices.split(",")
    chosen = choicesArr[randrange(len(choicesArr))]
    await client.send_message(message.channel, "{0}, я выбираю **{1}**".format(message.author.mention, chosen))


@client.event
async def on_message(message):
    if client.user == message.author:
        return
    elif message.content == (bot_prefix + "online"):
        await online(message)
    elif message.content.find(bot_prefix + "remove") != -1:
        num = message.content.replace("!remove ", "")
        await remove(message, num)
    elif message.content == (bot_prefix + "help"):
        await client.send_message(message.channel, help_menu)
    elif message.content.find(bot_prefix + "choice") != -1:
    	choices = message.content.replace("!choice ", "")
    	await choice(message, choices)


async def online(ctx):
    info = None
    try:
        reader, writer = await asyncio.open_connection(host='164.132.206.237', port=29000)
    except ConnectionRefusedError:
        await client.send_message(ctx.channel,
                                  embed=Embed(color=discord.Color.blue(), description="Сервер выключен"))
        return
    except TimeoutError:
        await client.send_message(ctx.channel,
                                  embed=Embed(color=discord.Color.blue(), description="Сервер выключен"))
        return
    writer.write(byte_array)
    try:
        info = await asyncio.wait_for(reader.read(2048), timeout=7)
    except asyncio.TimeoutError:
        await client.send_message(ctx.channel,
                                  embed=Embed(color=discord.Color.blue(), description="Сервер выключен"))
        return
    info = info.decode("cp437").split('\x00\x00\x00')
    len_players = str(info[4]).replace('\x00', '')
    max_players = str(info[5]).replace('\x00', '')
    await client.send_message(ctx.channel,
                              embed=Embed(color=discord.Color.blue(), description="На сервере **{0}**"
                              " из **{1}** человек".format(len_players, max_players)))


async def remove(ctx, number: str):
    # noinspection PyBroadException
    try:
        if not discord.Channel.permissions_for(ctx.channel,
                                               ctx.author).manage_messages and ctx.author.id:
            await client.send_message(ctx.channel,
                                      embed=Embed(color=discord.Color.red(), description="В доступе - отказано!"))
            await client.add_reaction(ctx, "❎")
            return
        mgs = []
        number = int(number)
        async for x in client.logs_from(ctx.channel, limit=number):
            mgs.append(x)
        await client.delete_messages(mgs)
        await client.send_message(ctx.channel, embed=Embed(color=discord.Color.blue(),
                                                                   description="🐾 {0} удалил **{1}** сообщений "
                                                                               "🐾".format(ctx.author.mention,
                                                                                          str(number))))
    except discord.ClientException:
        await client.send_message(ctx.channel, embed=Embed(color=discord.Color.red(),
                                                                   description="Ошибка! Количество сообщений должно "
                                                                               "быть не меньше, чем 2 и не должно "
                                                                               "превышать 100"))
    except discord.Forbidden:
        await client.send_message(ctx.channel, embed=Embed(color=discord.Color.red(),
                                                                   description="Ошибка! У бота недостаточно прав"))
    except:
        await client.send_message(ctx.channel,
                                  embed=Embed(color=discord.Color.red(), description="У вас недостаточно прав!!!"))


client.run(client_token)
