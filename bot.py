import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

# تحميل المتغيرات من .env
load_dotenv()
token = os.getenv('DISCORD_TOKEN')

# إنشاء البوت
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# حدث الاتصال
@bot.event
async def on_ready():
    print(f'{bot.user} متصل الآن! ✅')
    # تعيين حالة البوت
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="SAM"))

# أمر hello
@bot.command()
async def hello(ctx):
    await ctx.send(f'مرحباً {ctx.author.name}! 👋')

# أمر ping
@bot.command()
async def ping(ctx):
    await ctx.send(f'Pong! {round(bot.latency * 1000)}ms ⚡')

# أمر say
@bot.command()
async def say(ctx, *, text):
    await ctx.send(text)

# تشغيل البوت
bot.run(token)
