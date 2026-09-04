import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

# تحميل المتغيرات من .env
load_dotenv()
token = os.getenv('DISCORD_TOKEN')

# إنشاء البوت مع intents صحيح
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

# حدث الاتصال
@bot.event
async def on_ready():
    print(f'{bot.user} متصل الآن! ✅')
    await bot.change_presence(activity=discord.Game(name="!help"))

# حدث الرسالة
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    await bot.process_commands(message)

# أمر hello
@bot.command(name='hello')
async def hello(ctx):
    await ctx.send(f'مرحباً {ctx.author.name}! 👋')

# أمر ping
@bot.command(name='ping')
async def ping(ctx):
    await ctx.send(f'Pong! {round(bot.latency * 1000)}ms ⚡')

# أمر say
@bot.command(name='say')
async def say(ctx, *, message):
    await ctx.send(message)

# تشغيل البوت
bot.run(token)
