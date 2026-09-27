import discord
from discord.ext import commands
from discord.ui import Button, View, Modal, TextInput, UserSelect
from discord import app_commands
import datetime
import json
import os

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

LOG_FILE = "log_channels.json"

def load_log_channels():
    if not os.path.exists(LOG_FILE):
        return {}
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            return {int(k): v for k, v in json.load(f).items()}
    except Exception as e:
        print(f"Error loading logs: {e}")
        return {}

def save_log_channels(data):
    try:
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving logs: {e}")

log_channels = load_log_channels()
user_cooldowns = {}

class MessageModal(Modal, title="📝 ฝากบอก (Anonymous)"):
    feedback = TextInput(
        label="ข้อความที่ต้องการส่ง",
        style=discord.TextStyle.paragraph,
        placeholder="พิมพ์ความในใจที่นี่... (ไม่ระบุชื่อผู้ส่ง)",
        required=True,
        max_length=1800
    )
    
    image_url = TextInput(
        label="ลิงก์รูปภาพ (ถ้ามี)",
        style=discord.TextStyle.short,
        placeholder="https://example.com/image.png",
        required=False
    )

    def __init__(self, target_user: discord.Member):
        super().__init__()
        self.target_user = target_user

    async def on_submit(self, interaction: discord.Interaction):
        if self.target_user.bot:
            await interaction.response.send_message("❌ ไม่สามารถฝากบอกบอทได้ครับ", ephemeral=True)
            return
        
        if self.target_user.id == interaction.user.id:
            await interaction.response.send_message("❌ ไม่สามารถฝากบอกตัวเองได้ครับ", ephemeral=True)
            return

        server_name = interaction.guild.name
        server_icon = interaction.guild.icon.url if interaction.guild.icon else None
        message_content = self.feedback.value
        image_input = self.image_url.value
        
        embed = discord.Embed(
            title="📨 มีข้อความฝากบอกถึงคุณ (Anonymous)",
            description=f"จากเซิร์ฟเวอร์: **{server_name}**",
            color=0xf47fff, 
            timestamp=datetime.datetime.now()
        )
        
        if server_icon:
            embed.set_author(name=server_name, icon_url=server_icon)
            embed.set_thumbnail(url=server_icon)
        else:
            embed.set_author(name=server_name)

        embed.add_field(name="💬 ข้อความ:", value=f"```{message_content}```", inline=False)
        embed.set_footer(text="ระบบส่งข้อความแบบไม่ระบุตัวตน | ผู้รับไม่สามารถตอบกลับได้")
        
        if image_input:
            embed.set_image(url=image_input)

        try:
            await self.target_user.send(embed=embed)
            
            user_cooldowns[interaction.user.id] = datetime.datetime.now()

            success_embed = discord.Embed(
                title="✅ ส่งข้อความสำเร็จ!",
                description=f"ข้อความของคุณถูกส่งไปยัง {self.target_user.mention} เรียบร้อยแล้ว",
                color=0x57f287 
            )
            await interaction.response.send_message(embed=success_embed, ephemeral=True)

            guild_id = interaction.guild.id
            if guild_id in log_channels:
                log_channel_id = log_channels[guild_id]
                log_channel = interaction.guild.get_channel(log_channel_id)
                
                if log_channel:
                    now = datetime.datetime.now()
                    thai_year = now.year + 543
                    date_str = now.strftime(f'%d/%m/{thai_year} %H:%M')

                    log_embed = discord.Embed(
                        description=(
                            "## |  __บริการฝากบอก | สำเร็จแล้วค่ะ__\n\n"
                            "|  มีข้อความใหม่ถูกส่งผ่านระบบค่ะ !"
                        ),
                        color=0xffebb4
                    )
                    
                    log_embed.add_field(
                        name="• 🛹 **ผู้ทำรายการ**", 
                        value=f"↳ {interaction.user.mention}", 
                        inline=False
                    )
                    log_embed.add_field(
                        name="• 🏕 **ผู้รับข้อความ**", 
                        value=f"↳ {self.target_user.mention}", 
                        inline=False
                    )
                    log_embed.add_field(
                        name="• 💬 **ข้อความ**", 
                        value=f"↳ {message_content}", 
                        inline=False
                    )
                    
                    if image_input:
                        log_embed.add_field(name="• 🖼️ **รูปภาพ**", value=f"↳ [คลิกเพื่อดูรูป]({image_input})", inline=False)
                        log_embed.set_image(url=image_input)

                    log_embed.set_thumbnail(url=interaction.user.display_avatar.url)

                    log_embed.set_footer(text=f"ส่งเมื่อ • {date_str}", icon_url=interaction.user.display_avatar.url)
                    
                    await log_channel.send(embed=log_embed)

        except discord.Forbidden:
            await interaction.response.send_message(f"❌ ไม่สามารถส่งข้อความถึง {self.target_user.mention} ได้ (เขาอาจปิดรับ DM จากคนแปลกหน้า)", ephemeral=True)
        except Exception as e:
            if interaction.response.is_done():
                 await interaction.followup.send(f"❌ เกิดข้อผิดพลาด: {e}", ephemeral=True)
            else:
                 await interaction.response.send_message(f"❌ เกิดข้อผิดพลาด: {e}", ephemeral=True)

class UserSelectView(View):
    def __init__(self):
        super().__init__(timeout=120) 

    @discord.ui.select(cls=UserSelect, placeholder="🔍 เลือกคนที่ต้องการฝากบอก...", min_values=1, max_values=1)
    async def select_callback(self, interaction: discord.Interaction, select: UserSelect):
        target_user = select.values[0]
        
        if target_user.bot:
            await interaction.response.send_message("❌ ไม่สามารถฝากบอกบอทได้ครับ", ephemeral=True)
            return
        
        if target_user.id == interaction.user.id:
            await interaction.response.send_message("❌ ไม่สามารถฝากบอกตัวเองได้ครับ (เหงาเหรอ?)", ephemeral=True)
            return

        await interaction.response.send_modal(MessageModal(target_user))

class FakBokView(View):
    def __init__(self):
        super().__init__(timeout=None) 

    @discord.ui.button(label="เริ่มใช้งานฝากบอก", style=discord.ButtonStyle.primary, emoji="💌", custom_id="fakbok_btn_primary")
    async def fakbok_button(self, interaction: discord.Interaction, button: Button):
        user_id = interaction.user.id
        if user_id in user_cooldowns:
            last_used = user_cooldowns[user_id]
            now = datetime.datetime.now()
            duration = datetime.timedelta(minutes=5)
            
            if now - last_used < duration:
                retry_after = duration - (now - last_used)
                minutes = int(retry_after.total_seconds() // 60)
                seconds = int(retry_after.total_seconds() % 60)
                
                await interaction.response.send_message(
                    f"⏳ **ใจเย็นก่อนวัยรุ่น!** คุณติด Cooldown อยู่\nกรุณารออีก `{minutes} นาที {seconds} วินาที` ถึงจะส่งได้อีกครั้งครับ", 
                    ephemeral=True
                )
                return

        embed = discord.Embed(
            title="👤 เลือกผู้รับข้อความ",
            description="กรุณาเลือกรายชื่อสมาชิกที่คุณต้องการฝากบอกจากเมนูด้านล่างนี้ 👇",
            color=0x5865F2
        )
        await interaction.response.send_message(embed=embed, view=UserSelectView(), ephemeral=True)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    try:
        bot.add_view(FakBokView()) 
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

@bot.tree.command(name="setup_fakbok", description="ติดตั้งระบบฝากบอก (Admin Only)")
@app_commands.checks.has_permissions(administrator=True)
async def setup_fakbok(interaction: discord.Interaction):
    embed = discord.Embed(
        title="📮 บริการรับฝากบอก (Anonymous Message)",
        description=(
            "ยินดีต้อนรับสู่บริการฝากบอก!\n\n"
            "☁️ **ส่งข้อความหาใครก็ได้แบบไม่ระบุตัวตน**\n"
            "☁️ **ปลอดภัยและเป็นความลับ**\n\n"
            "👇 **กดปุ่มด้านล่างเพื่อเริ่มส่งข้อความ**"
        ),
        color=0xf47fff 
    )

    embed.set_image(url="https://cdn.discordapp.com/attachments/1460238820208279609/1465397416667644076/eb9c265a05933d10bb50ba92830f96c7.jpg?ex=6978f531&is=6977a3b1&hm=c22ba2fe2f0f1d0ef76a1d5fec3cf4d96e90c35301fe609191ddfd554457809c&")

    await interaction.response.send_message(embed=embed, view=FakBokView())

@bot.tree.command(name="set_log", description="ตั้งค่าห้องสำหรับเก็บ Log การฝากบอก (Admin Only)")
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(channel="เลือกห้องข้อความที่ต้องการให้แจ้งเตือน Log")
async def set_log(interaction: discord.Interaction, channel: discord.TextChannel):
    log_channels[interaction.guild.id] = channel.id
    save_log_channels(log_channels)
    
    embed = discord.Embed(
        title="✅ ตั้งค่าห้อง Log สําเร็จ",
        description=f"ระบบจะส่ง Log การฝากบอกไปที่ห้อง {channel.mention}\n(บันทึกการตั้งค่าลงไฟล์ log_channels.json แล้ว)",
        color=0x57f287
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)

bot.run("โทเคนของมึง")