import nextcord
from nextcord.ext import commands
from dotenv import load_dotenv
import os

# โหลดค่าจากไฟล์ .env
load_dotenv()

# ดึง Token มาเก็บไว้ในตัวแปร
token = os.getenv("waguri_token")

intents = nextcord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.all()

bot = commands.Bot(command_prefix='!', help_command=None, intents=intents)

BotSever1 = 1551460858197053502  # ไอดี เซิฟเวอร์ดิสคอส
BotSever2 = 1552241991654576149  # ไอดี ห้องที่จะให้บอทลง

@bot.event
async def on_ready():
    await bot.change_presence(activity=nextcord.Streaming(
        name="รับทำบอท", url="https://www.discord.com"))
    vc = nextcord.utils.get(bot.get_guild(BotSever1).channels, id=BotSever2)
    await vc.guild.change_voice_state(channel=vc, self_mute=False, self_deaf=True)
    print('Bot is ready.')

@bot.event
async def on_voice_state_update(member, before, after):
   
    if after.channel and after.self_stream:
        print(f'{member.name} is in {after.channel.name} and started speaking.')

bot.run(token)