import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import json
from datetime import datetime, timedelta

# تحميل المتغيرات من .env
load_dotenv()
token = os.getenv('DISCORD_TOKEN')

# إنشاء البوت
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# متغير لحفظ بيانات XP
xp_data = {}
xp_roles = {}

# تحميل البيانات من ملف
def load_data():
    global xp_data, xp_roles
    try:
        with open('xp_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            xp_data = data.get('xp_data', {})
            xp_roles = data.get('xp_roles', {})
    except FileNotFoundError:
        pass

# حفظ البيانات في ملف
def save_data():
    with open('xp_data.json', 'w', encoding='utf-8') as f:
        json.dump({'xp_data': xp_data, 'xp_roles': xp_roles}, f, ensure_ascii=False, indent=4)

# حدث الاتصال
@bot.event
async def on_ready():
    print(f'{bot.user} متصل الآن! ✅')
    load_data()
    # تعيين حالة البوت - Streaming مع حالة Do Not Disturb (أحمر)
    await bot.change_presence(status=discord.Status.do_not_disturb, activity=discord.Streaming(name="SAM", url="https://www.twitch.tv/"))

# حدث عند إرسال رسالة
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    if message.author.bot:
        return
    
    # فحص ما إذا كان المستخدم لديه رتبة XP
    guild_id = str(message.guild.id) if message.guild else None
    if guild_id and guild_id in xp_roles:
        role_id = int(xp_roles[guild_id])
        role = message.guild.get_role(role_id)
        
        if role and role in message.author.roles:
            user_id = str(message.author.id)
            
            # إنشاء مفتاح فريد للمستخدم والأسبوع
            week_key = f"{user_id}_{guild_id}_{get_week_number()}"
            
            if week_key not in xp_data:
                xp_data[week_key] = {'messages': 0, 'xp': 0}
            
            xp_data[week_key]['messages'] += 1
            
            # إضافة XP كل 10 رسائل
            if xp_data[week_key]['messages'] % 10 == 0:
                xp_data[week_key]['xp'] += 5
                save_data()
    
    await bot.process_commands(message)

# دالة للحصول على رقم الأسبوع
def get_week_number():
    return datetime.now().isocalendar()[1]

# دالة لحساب المستوى من XP
def calculate_level(xp):
    return xp // 5

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

# أمر setup
@bot.command()
@commands.has_permissions(administrator=True)
async def setup(ctx):
    """أمر إداري لتحديد رتبة XP"""
    embed = discord.Embed(
        title="⚙️ إعدادات XP",
        description="من فضلك اذكر الرتبة اللي تبي تحسب XP حقها",
        color=discord.Color.blue()
    )
    msg = await ctx.send(embed=embed)
    
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel
    
    try:
        response = await bot.wait_for('message', timeout=60.0, check=check)
        
        # فحص المنشنات
        if response.mentions:
            await ctx.send("من فضلك اذكر رتبة وليس يوزر! ❌")
            return
        
        # محاولة الحصول على الرتبة
        role = None
        
        # البحث عن الرتبة حسب الاسم
        for r in ctx.guild.roles:
            if r.name.lower() == response.content.lower():
                role = r
                break
        
        # إذا لم يجد، حاول تحليل ID
        if not role and response.content.isdigit():
            role = ctx.guild.get_role(int(response.content))
        
        if not role:
            await ctx.send("ما لقيت الرتبة! ❌")
            return
        
        # حفظ الرتبة
        guild_id = str(ctx.guild.id)
        xp_roles[guild_id] = str(role.id)
        save_data()
        
        # الرد بـ ✅
        await ctx.send(f"✅ تم حفظ الرتبة: {role.mention}")
        
    except:
        await ctx.send("انتهت المهلة الزمنية! ⏱️")

# أمر xp
@bot.command()
async def xp(ctx):
    """عرض ترتيب XP للرتبة المحددة"""
    guild_id = str(ctx.guild.id)
    
    if guild_id not in xp_roles:
        await ctx.send("لم يتم إعداد رتبة XP بعد! استخدم `!setup` أولاً.")
        return
    
    role_id = int(xp_roles[guild_id])
    role = ctx.guild.get_role(role_id)
    
    if not role:
        await ctx.send("الرتبة المحفوظة لم تعد موجودة! ❌")
        return
    
    # جمع بيانات XP للأسبوع الحالي
    week_number = get_week_number()
    leaderboard = []
    
    for user_id_str in xp_data.keys():
        user_id_parts = user_id_str.split('_')
        if len(user_id_parts) >= 3:
            user_id = int(user_id_parts[0])
            data_guild_id = user_id_parts[1]
            data_week = int(user_id_parts[2])
            
            if data_guild_id == guild_id and data_week == week_number:
                try:
                    user = await bot.fetch_user(user_id)
                    leaderboard.append({
                        'user': user,
                        'xp': xp_data[user_id_str]['xp']
                    })
                except:
                    pass
    
    # ترتيب حسب XP
    leaderboard.sort(key=lambda x: x['xp'], reverse=True)
    
    # إنشاء Embed
    embed = discord.Embed(
        color=role.color if role.color != discord.Color.default() else discord.Color.gold()
    )
    
    if not leaderboard:
        embed.description = "لا يوجد بيانات XP حالياً!"
        await ctx.send(embed=embed)
        return
    
    # بناء الـ leaderboard
    leaderboard_text = "## <:voice:1311747451778105415> أفضل نقاط الكتابة\n"
    
    for idx, entry in enumerate(leaderboard[:5], 1):
        level = calculate_level(entry['xp'])
        emoji = "🔹" if idx == 1 else "🔸"
        bold = "**" if idx == 1 else ""
        
        if idx == 1:
            leaderboard_text += f"{emoji} {bold}| #{idx}{bold} <@!{entry['user'].id}> - خبرة: **{entry['xp']}** `|` مستوى: **{level}**\n"
        else:
            leaderboard_text += f"{emoji} | #{idx} <@!{entry['user'].id}> - خبرة: **{entry['xp']}** `|` مستوى: **{level}**\n"
    
    # إضافة آخر شخص في الترتيب
    if len(leaderboard) > 5:
        last_entry = leaderboard[-1]
        last_level = calculate_level(last_entry['xp'])
        leaderboard_text += f"🔹 **| #{len(leaderboard)}** <@!{last_entry['user'].id}> - خبرة: **{last_entry['xp']}** `|` مستوى: **{last_level}**\n"
    
    # إضافة ملاحظة التصفير
    next_monday = datetime.now() + timedelta(days=(7 - datetime.now().weekday()))
    next_monday_timestamp = int(next_monday.timestamp())
    
    leaderboard_text += f"\n-# يتم تصفير التوب الأسبوعي كل يوم الاثنين. سيتم التصفير خلال <t:{next_monday_timestamp}:R>"
    
    embed.description = leaderboard_text
    
    await ctx.send(embed=embed)

# تشغيل البوت
import asyncio
bot.run(token)
