from datetime import datetime
import os
import discord
from dotenv import load_dotenv
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.guilds = True
bot = commands.Bot(command_prefix='>',
                   sync_commands_debug=True,
                   sync_commands=True,
                   activity=discord.Activity(type=discord.ActivityType.playing,
                                             name="неплохие разработки",
                                             application_id=1296968381156556841,
                                             buttons=[{"label": "Click me", "url": "https://example.com"}],
                                             timestamps={"start": "1507543514"},
                                             assets={"large_image": "1211841789909823538", "large_text": "Wi"}),
                   intents=intents)

load_dotenv()
SHUTDOWN_COMMAND = os.getenv("SHUTDOWN_COMMAND")
SHUTDOWN_USER = os.getenv("SHUTDOWN_USER")
SHUTDOWN_DENIED_RESPONSE = os.getenv("SHUTDOWN_DENIED_RESPONSE")

LAST_USER = ""
LAST_MESSAGE = ""
LAST_REACTION = ""


def get_message_link(reaction):
    channel = reaction.message.channel
    guild_id = reaction.message.guild.id
    channel_id = reaction.message.channel.id
    message_id = reaction.message.id
    message_url = f"https://discord.com/channels/{guild_id}/{channel_id}/{message_id}"

    return message_url


def get_link_by_message(message):
    return f"https://discord.com/channels/{message.guild.id}/{message.channel.id}/{message.id}"


@bot.event
async def on_ready():
    print(f'Bot Name: {bot.user}')
    try:
        synced = await bot.tree.sync()
        print(f'Добавлено {len(synced)} команд')
    except Exception as e:
        print(e)


@bot.command(name='add_cookies')
async def add_cookie_reactions(ctx):
    # Получаем последние 10 сообщений из истории
    async for message in ctx.channel.history(limit=1):
        try:
            await message.add_reaction("🍪")  # Добавляем реакцию к сообщению
        except discord.HTTPException as e:
            print(f'Не удалось добавить реакцию к сообщению {message.id}: {e}')
    await ctx.send('Раздача печенек на спавне прошла успешно')
    await ctx.send('<:molor:1297539405585846303>')


@bot.command(name='find_cookies')
async def find_cookie_reactions(ctx):
    # channel = bot.get_channel(1271061832412696631)
    channel = ctx.channel
    cookies = False
    async for message in channel.history(limit=500):
        # Проверяем, есть ли у сообщения реакция :cookie:
        for reaction in message.reactions:
            if str(reaction.emoji) == "🍪":  # Проверяем реакцию на :cookie:
                cookies = True
                # Получаем пользователей, которые поставили эту реакцию
                users = []
                async for user in reaction.users():
                    users.append(user)
                user_names = ', '.join(user.name for user in users)
                message_url = get_message_link(reaction)
                await ctx.send(
                    f'По записям камер наблюдения я обнаружил злоумышленника {user_names}, который ставил печены к [этому сообщению]({message_url})')
    if not cookies:
        await ctx.send(f'По записям камер видеонаблюдения я не нашёл злоумышленников, которые ставили печены')
    else:
        await ctx.send(f'Дело передал в печенную полицию, сказали начнут расследование')


@bot.command(name='find_cookies_date')
async def find_cookie_reactions(ctx, date: str):
    # Преобразование строки даты в объект datetime
    try:
        search_date = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        await ctx.send("Неверный формат даты. Используйте формат YYYY-MM-DD.")
        return

    channel = ctx.channel
    cookies = False

    async for message in channel.history(limit=700):
        print(message.created_at.date())
        # Проверяем, совпадает ли дата сообщения с искомой
        if message.created_at.date() == search_date:
            # Проверяем, есть ли у сообщения реакция :cookie:
            for reaction in message.reactions:
                if str(reaction.emoji) == "🍪":  # Проверяем реакцию на :cookie:
                    cookies = True
                    # Получаем пользователей, которые поставили эту реакцию
                    users = []
                    async for user in reaction.users():
                        users.append(user)
                    user_names = ', '.join(user.name for user in users)
                    message_url = get_link_by_message(message)
                    await ctx.send(
                        f'По записям камер наблюдения я обнаружил злоумышленника {user_names}, который ставил печеньки к [этому сообщению]({message_url})')

    if not cookies:
        await ctx.send(f'По записям камер видеонаблюдения я не нашёл злоумышленников, которые ставили печеньки.')
    else:
        await ctx.send(f'Дело передал в печенную полицию, сказали начнут расследование.')


@bot.event
async def on_reaction_add(reaction, user):
    global LAST_MESSAGE
    global LAST_USER
    global LAST_REACTION
    print(f'Reaction {reaction.emoji} added by {user.name} to message {reaction.message.id}')
    if str(reaction.emoji) == "🍪":
        if LAST_MESSAGE != reaction.message.id or LAST_USER != user.name or LAST_REACTION != str(reaction.emoji):
            print(user.name)
            LAST_REACTION = str(reaction.emoji)
            LAST_USER = user.name
            LAST_MESSAGE = reaction.message.id
            channel = reaction.message.channel
            guild_id = reaction.message.guild.id
            channel_id = reaction.message.channel.id
            message_id = reaction.message.id
            message_url = f"https://discord.com/channels/{guild_id}/{channel_id}/{message_id}"
            await channel.send(f'{user.name} добавил реакцию {reaction.emoji} к [этому сообщению]({message_url})')


# Обработчик события при получении сообщения
@bot.event
async def on_message(message):
    # Игнорируем сообщения от самого бота
    if message.author == bot.user:
        return

    if message.content == SHUTDOWN_COMMAND:
        if str(message.author) == SHUTDOWN_USER:
            await message.channel.send('Завершение работы бота')
            await bot.close()
        else:
            await message.channel.send(SHUTDOWN_DENIED_RESPONSE)

    # Простой ответ на определенные сообщения
    if "а что такое как ты стал ботом" in message.content.lower():
        await message.channel.send("https://cdn.nekotina.com/images/7W-hc3VF.gif")

    # Позволяем другим обработчикам обрабатывать это сообщение
    await bot.process_commands(message)


token = os.getenv("TOKEN")
bot.run(token, reconnect=True)
