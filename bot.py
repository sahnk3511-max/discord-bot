import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

# تحميل المتغيرات من .env
load_dotenv()
token = os.getenv('DISCORD_TOKEN')

# إنشاء البوت
bot = commands.Bot(command_prefix='!')

# حدث الاتصال
@bot.event
async def on_ready():
    print(f'{bot.user} متصل الآن! ✅')

# أمر بسيط
@bot.command(name='hello')
async def hello(ctx):
    await ctx.send(f'مرحباً {ctx.author.name}! 👋')

# أمر ping
@bot.command(name='ping')
async def ping(ctx):
    await ctx.send(f'Pong! {round(bot.latency * 1000)}ms ⚡')

# تشغيل البوت
bot.run(token)
