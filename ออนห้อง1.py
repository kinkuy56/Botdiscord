import nextcord
from nextcord.ext import commands
from dotenv import load_dotenv
import os

# โหลดค่าจากไฟล์ .env
load_dotenv()

# ดึง Token มาเก็บไว้ในตัวแปร (เปลี่ยนเป็น momo_token)
token = os.getenv("mea_token")

# ตรวจสอบว่ามี Token หรือไม่
if not token:
    print("❌ ไม่พบ Token ในไฟล์ .env (momo_token)")
    exit()

intents = nextcord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix='!', help_command=None, intents=intents)

BotSever1 = 1551460858197053502  # ไอดี เซิร์ฟเวอร์ดิสคอร์ด
BotSever2 = 1552241991654576149  # ไอดี ห้องเสียงที่จะให้บอทเข้า

# ตัวแปรป้องกันการรัน on_ready ซ้ำตอน reconnect
_has_joined_voice = False

@bot.event
async def on_ready():
    global _has_joined_voice
    print(f'✅ บอทพร้อมใช้งาน: {bot.user}')

    # ตั้งสถานะบอท
    await bot.change_presence(activity=nextcord.Streaming(
        name="รับทำบอท", url="https://www.discord.com"))

    # ถ้าเคยเข้า voice ไปแล้ว ให้ข้ามการเข้าซ้ำ
    if _has_joined_voice:
        return

    try:
        guild = bot.get_guild(BotSever1)
        if guild:
            channel = guild.get_channel(BotSever2)
            # ตรวจสอบว่าเป็นห้องเสียงจริงๆ
            if isinstance(channel, nextcord.VoiceChannel):
                vc = await channel.connect()
                await vc.guild.change_voice_state(channel=channel, self_mute=False, self_deaf=True)
                _has_joined_voice = True
                print(f"🔊 เข้าห้องเสียงแล้ว: {channel.name}")
            else:
                print(f"⚠️ ไอดี {BotSever2} ไม่ใช่ห้องเสียง หรือไม่พบห้อง")
        else:
            print(f"⚠️ ไม่พบเซิร์ฟเวอร์ไอดี {BotSever1}")
    except Exception as e:
        print(f"❌ Error joining voice channel: {e}")

@bot.event
async def on_voice_state_update(member, before, after):
    # ตรวจสอบว่ามีการแชร์หน้าจอ (Stream) หรือไม่
    if after.channel and after.self_stream:
        print(f'📺 {member.name} กำลังแชร์หน้าจอใน {after.channel.name}')
    
    # [ทางเลือก] ถ้าต้องการเช็คตอน "พูด" ให้ใช้โค้ดด้านล่างนี้แทน
    # if before.self_mute != after.self_mute and not after.self_mute:
    #     print(f'🎤 {member.name} เริ่มพูดใน {after.channel.name}')

@bot.event
async def on_disconnect():
    print("⚠️ บอทหลุดการเชื่อมต่อ กำลังพยายามเชื่อมต่อใหม่...")

# รันบอท
if __name__ == "__main__":
    bot.run(token)
