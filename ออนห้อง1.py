import nextcord
from nextcord.ext import commands
from dotenv import load_dotenv
import os

# โหลดค่าจากไฟล์ .env
load_dotenv()

# ดึง Token มาเก็บไว้ในตัวแปร (หรือจะใส่ Token จริงๆ เป็นข้อความแทนตรงนี้ก็ได้)
token = os.getenv("waguri_token")

intents = nextcord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix='!', help_command=None, intents=intents)

BotSever1 = 1551460858197053502  # ไอดี เซิฟเวอร์ดิสคอร์ด
BotSever2 = 1552241991654576149  # ไอดี ห้องที่จะให้บอทลง

@bot.event
async def on_ready():
    await bot.change_presence(activity=nextcord.Streaming(
        name="รับทำบอท", url="https://www.discord.com"))
    try:
        guild = bot.get_guild(BotSever1)
        if guild:
            vc = nextcord.utils.get(guild.channels, id=BotSever2)
            if vc:
                await vc.guild.change_voice_state(channel=vc, self_mute=False, self_deaf=True)
    except Exception as e:
        print(f"Error joining voice channel: {e}")
    print('Bot is ready.')

@bot.event
async def on_voice_state_update(member, before, after):
    if after.channel and after.self_stream:
        print(f'{member.name} is in {after.channel.name} and started speaking.')

bot.run(token)
