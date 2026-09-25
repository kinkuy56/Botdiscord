import nextcord
from nextcord.ext import commands
from dotenv import load_dotenv
import os
import asyncio

# โหลดค่าจากไฟล์ .env
load_dotenv()

# ดึง Token มาเก็บไว้ในตัวแปร (สามารถเปลี่ยนเป็นใส่ Token ตรงๆ ได้เช่น "MTM...")
TOKEN = os.getenv("ticket_token")

# ตั้งค่า Intents ของบอท (ใช้ nextcord)
intents = nextcord.Intents.default()
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)


# ============================================================
#  📋 หัวข้อ Ticket ที่ให้เลือก
# ============================================================
TICKET_TOPICS = {
    "contact_admin": {"label": "ติดต่อแอดมิน", "emoji": "🎟️", "description": "คุยกับแอดมินโดยตรง"},
    "buy_product": {"label": "ซื้อของ", "emoji": "🛒", "description": "สั่งซื้อสินค้าในร้าน"},
    "topup": {"label": "เติมเงิน", "emoji": "💰", "description": "แจ้งขอเติมเงิน"},
    "ask": {"label": "สอบถาม", "emoji": "❓", "description": "สอบถามข้อมูลทั่วไป"},
    "report": {"label": "แจ้งปัญหา", "emoji": "🚨", "description": "แจ้งปัญหาหรือข้อผิดพลาด"},
}


# ============================================================
#  🔒 View: ปุ่มปิด Ticket
# ============================================================
class CloseView(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @nextcord.ui.button(label="🔒 ปิด Ticket", style=nextcord.ButtonStyle.danger, custom_id="close_ticket_btn")
    async def close_ticket(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.response.send_message("กำลังปิดห้องนี้ใน 5 วินาที...", ephemeral=False)
        await asyncio.sleep(5)
        try:
            await interaction.channel.delete()
        except Exception as e:
            print(f"เกิดข้อผิดพลาดในการลบห้อง: {e}")


# ============================================================
#  📋 View: เมนูเลือกหัวข้อ
# ============================================================
class TopicSelectView(nextcord.ui.View):
    def __init__(self, member: nextcord.Member):
        super().__init__(timeout=60)
        self.member = member

        options = [
            nextcord.SelectOption(label=info["label"], emoji=info["emoji"], description=info["description"], value=code)
            for code, info in TICKET_TOPICS.items()
        ]

        self.select = nextcord.ui.Select(placeholder="📌 เลือกหัวข้อที่คุณต้องการติดต่อ", min_values=1, max_values=1, options=options, custom_id="ticket_topic_select")
        self.select.callback = self.on_select
        self.add_item(self.select)

    async def on_select(self, interaction: nextcord.Interaction):
        if interaction.user.id != self.member.id:
            return await interaction.response.send_message("❌ เมนูนี้ไม่ใช่ของคุณ กรุณากดปุ่มเปิด Ticket เอง", ephemeral=True)

        guild = interaction.guild
        member = interaction.user
        topic_code = self.select.values[0]
        topic = TICKET_TOPICS[topic_code]

        existing_channel = nextcord.utils.get(guild.text_channels, name=f"ticket-{member.name.lower()}")
        if existing_channel:
            return await interaction.response.send_message(f"คุณมีห้อง Ticket เปิดอยู่แล้ว: {existing_channel.mention}", ephemeral=True)

        overwrites = {
            guild.default_role: nextcord.PermissionOverwrite(view_channel=False),
            member: nextcord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            guild.me: nextcord.PermissionOverwrite(view_channel=True, send_messages=True, manage_channels=True),
        }

        category = interaction.channel.category
        ticket_channel = await guild.create_text_channel(
            name=f"ticket-{topic_code}-{member.name}".lower()[:100],
            category=category, overwrites=overwrites,
            topic=f"Ticket [{topic['label']}] ของ {member.id}"
        )

        embed = nextcord.Embed(
            title=f"{topic['emoji']} Ticket: {topic['label']}",
            description=f"สวัสดีคุณ {member.mention}\nหัวข้อ: **{topic['label']}**\n\nทีมงานจะเข้ามาช่วยเหลือโดยเร็วที่สุด\nกรุณาพิมพ์รายละเอียดไว้ได้เลยครับ",
            color=nextcord.Color.green()
        )
        await ticket_channel.send(embed=embed, view=CloseView())
        await interaction.response.send_message(f"✅ สร้างห้อง Ticket ให้คุณแล้วครับ: {ticket_channel.mention}", ephemeral=True)


# ============================================================
#  🎫 View: ปุ่มเปิด Ticket (หน้าหลัก)
# ============================================================
class TicketView(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @nextcord.ui.button(label="🎫 เปิด Ticket", style=nextcord.ButtonStyle.primary, custom_id="open_ticket_btn")
    async def create_ticket(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        guild = interaction.guild
        member = interaction.user

        existing_channel = nextcord.utils.get(guild.text_channels, name=f"ticket-{member.name.lower()}")
        if existing_channel:
            return await interaction.response.send_message(f"คุณมีห้อง Ticket เปิดอยู่แล้ว: {existing_channel.mention}", ephemeral=True)

        embed = nextcord.Embed(
            title="📌 เลือกหัวข้อที่ต้องการติดต่อ",
            description="กรุณาเลือกหัวข้อจากเมนูด้านล่างครับ",
            color=nextcord.Color.blue()
        )
        await interaction.response.send_message(embed=embed, view=TopicSelectView(member), ephemeral=True)


# ============================================================
#  🚀 Events & Commands
# ============================================================
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name} (ID: {bot.user.id})")
    print("Bot is ready!")


@bot.command(name="setup")
@commands.has_permissions(administrator=True)
async def setup(ctx):
    embed = nextcord.Embed(
        title="ระบบแจ้งปัญหา / ติดต่อทีมงาน (Support Ticket)",
        description="กดปุ่มด้านล่างนี้เพื่อเปิดห้องพูดคุยกับทีมงานส่วนตัวครับ",
        color=nextcord.Color.blue()
    )

    # ✅ ลบ Panel เก่าที่บอทเคยส่งก่อนหน้า
    async for message in ctx.channel.history(limit=50):
        if message.author == bot.user and message.embeds:
            if message.embeds[0].title and "Support Ticket" in message.embeds[0].title:
                try:
                    await message.delete()
                except:
                    pass

    await ctx.send(embed=embed, view=TicketView())
    try:
        await ctx.message.delete()
    except:
        pass


bot.run(TOKEN)
