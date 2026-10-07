import nextcord
from nextcord.ext import commands
from dotenv import load_dotenv
import os
import sys

# โหลดค่าจากไฟล์ .env
load_dotenv()

# ดึง Token
token = os.getenv("momo_token")

# ตรวจสอบ token ก่อนรัน
if not token:
    print("❌ ไม่พบ token ในตัวแปร momo_token กรุณาตรวจสอบ .env หรือ Environment Variables")
    sys.exit(1)

if not isinstance(token, str) or len(token) < 50:
    print(f"❌ token ดูผิดปกติ (length={len(token) if token else 0}) กรุณาตรวจสอบอีกครั้ง")
    sys.exit(1)

intents = nextcord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.members = True  # ต้องเปิดใน Discord Developer Portal ด้วย

bot = commands.Bot(command_prefix='!', help_command=None, intents=intents)

BotSever1 = 1551460858197053502  # ไอดี เซิร์ฟเวอร์ดิสคอร์ด
BotSever2 = 1552241991654576149  # ไอดี ห้องที่จะให้บอทลง

# flag กัน on_ready รันซ้ำตอน reconnect
_ready_done = False


@bot.event
async def on_ready():
    global _ready_done

    await bot.change_presence(activity=nextcord.Streaming(
        name="รับทำบอท", url="https://www.discord.com"))

    # ป้องกัน join voice ซ้ำตอน reconnect
    if _ready_done:
        print(f'Bot reconnected as {bot.user}')
        return
    _ready_done = True

    print(f'Bot is ready. Logged in as {bot.user} (ID: {bot.user.id})')

    # รอ cache โหลด guild เสร็จ
    await bot.wait_until_ready()

    try:
        guild = bot.get_guild(BotSever1)
        if not guild:
            print(f"⚠️ หาเซิร์ฟเวอร์ ID {BotSever1} ไม่เจอ (บอทอาจยังไม่ถูกเชิญเข้า)")
            return

        vc = guild.get_channel(BotSever2)
        if not vc:
            print(f"⚠️ หาห้อง ID {BotSever2} ไม่เจอ")
            return

        if not isinstance(vc, nextcord.VoiceChannel):
            print(f"⚠️ ID {BotSever2} ไม่ใช่ห้องเสียง")
            return

        # ถ้าบอทอยู่ในห้องนี้อยู่แล้ว ไม่ต้อง join ซ้ำ
        if guild.voice_client and guild.voice_client.channel.id == vc.id:
            print(f"บอทอยู่ในห้อง {vc.name} แล้ว")
            return

        await vc.connect(self_mute=False, self_deaf=True)
        print(f"✅ เข้าห้องเสียง {vc.name} สำเร็จ")

    except nextcord.errors.HTTPException as e:
        print(f"❌ HTTP error ตอนเข้าห้องเสียง: {e.status} - {e.text}")
    except Exception as e:
        print(f"❌ Error joining voice channel: {type(e).__name__}: {e}")


@bot.event
async def on_voice_state_update(member, before, after):
    # ข้าม event ของบอทตัวเอง
    if member.bot:
        return

    if after.channel and after.self_stream:
        print(f'{member.name} is in {after.channel.name} and started streaming.')


@bot.event
async def on_error(event, *args, **kwargs):
    print(f"⚠️ Error in event {event}")
    import traceback
    traceback.print_exc()


def main():
    try:
        bot.run(token)
    except nextcord.errors.HTTPException as e:
        if e.status == 429:
            print("❌ โดน rate limit (429) จาก Discord")
            print("   → รอ 30 นาที - 1 ชม. แล้วลองใหม่")
            print("   → หรือลดจำนวนบอทที่รันพร้อมกัน")
        elif e.status == 401:
            print("❌ Token ไม่ถูกต้อง (401 Unauthorized)")
        else:
            print(f"❌ HTTP error: {e.status} - {e.text}")
        sys.exit(1)
    except nextcord.errors.LoginFailure:
        print("❌ Token ไม่ถูกต้อง (LoginFailure)")
        sys.exit(1)
    except KeyboardInterrupt:
        print("ปิดบอทด้วยตัวเอง")
    except Exception as e:
        print(f"❌ Error ไม่คาดคิด: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
