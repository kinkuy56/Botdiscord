import nextcord
import json 
from nextcord.ext import commands, tasks
from nextcord import Interaction, ButtonStyle, Embed
from nextcord.ui import button, Modal, TextInput
import os
import datetime
import random
from collections import defaultdict, deque

intents = nextcord.Intents.default()
intents.message_content = True
intents.members = True  
intents.guilds = True
intents.bans = True
bot = commands.Bot(command_prefix=".", intents=intents)

# CONFIG Main
TOKEN = os.getenv('DISCORD_TOKEN')

owner_user = "jarya_dang"
COLOR = 0xffb6c1  # สีชมพูอ่อนพาสเทลเข้ากับ Waguri
hosting_name = 'แหนม'

# 🎞️ ลิงก์ภาพเคลื่อนไหวเมนูเซฟยศ
Animated_Image = 'https://cdn.discordapp.com/attachments/1168170116383522817/1552008477432356874/kaoruko-waguri-waguri-kaoruko.gif?ex=6ab40c07&is=6ab2ba87&hm=523ce1235101c280bd85f9136400e28ff3f815b04b6ba82b706023269fcf70ec&'

# ==========================================
# 🛡️ ระบบกันยิงดิส & แอนตี้สแปม (ลบข้อความย้อนหลัง + Timeout 15 วิ)
# ==========================================
spam_tracker = defaultdict(deque)
channel_delete_tracker = defaultdict(deque)
ban_kick_tracker = defaultdict(deque)

LOG_CHANNEL_NAME = "บอท-log"  

async def send_security_log(guild, title, description):
    log_channel = nextcord.utils.get(guild.text_channels, name=LOG_CHANNEL_NAME)
    if log_channel:
        embed = Embed(title=f"🚨 [Anti-Nuke/Spam Alert] {title}", description=description, color=0xff0000)
        embed.timestamp = datetime.datetime.now()
        await log_channel.send(embed=embed)

# 1. ป้องกันการลบห้อง (>= 10 ห้องภายใน 10 วินาที)
@bot.event
async def on_guild_channel_delete(channel):
    guild = channel.guild
    try:
        async for entry in guild.audit_logs(limit=1, action=nextcord.AuditLogAction.channel_delete):
            user = entry.user
            if not user or user.bot or user.id == guild.owner_id:
                return
            
            now = datetime.datetime.now()
            channel_delete_tracker[user.id].append(now)
            
            while channel_delete_tracker[user.id] and (now - channel_delete_tracker[user.id][0]).total_seconds() > 10:
                channel_delete_tracker[user.id].popleft()
                
            if len(channel_delete_tracker[user.id]) >= 10:
                member = guild.get_member(user.id)
                if member:
                    try:
                        await member.kick(reason="Anti-Nuke: พยายามลบห้องจำนวนมากผิดปกติ (>= 10 ห้อง)")
                        await send_security_log(guild, "ตรวจพบการลบห้องผิดปกติ!", f"ผู้ใช้ `{user}` ทำการลบห้องถึง 10 ห้องรัวๆ บอทได้ทำการเตะออกจากเซิร์ฟเวอร์แล้ว!")
                    except Exception:
                        pass
    except Exception:
        pass

# 2. ป้องกันการแบนสมาชิกยกลิ้ง (>= 3 คนภายใน 10 วินาที)
@bot.event
async def on_member_ban(guild, user):
    try:
        async for entry in guild.audit_logs(limit=1, action=nextcord.AuditLogAction.ban):
            actor = entry.user
            if not actor or actor.bot or actor.id == guild.owner_id:
                return
            
            now = datetime.datetime.now()
            ban_kick_tracker[actor.id].append(now)
            
            while ban_kick_tracker[actor.id] and (now - ban_kick_tracker[actor.id][0]).total_seconds() > 10:
                ban_kick_tracker[actor.id].popleft()
                
            if len(ban_kick_tracker[actor.id]) >= 3: 
                member = guild.get_member(actor.id)
                if member:
                    try:
                        await member.ban(reason="Anti-Nuke: พยายามแบนสมาชิกจำนวนมาก")
                        await send_security_log(guild, "ตรวจพบการแบนสมาชิกยกลิ้ง!", f"ผู้ใช้ `{actor}` ทำการแบนคนรัวๆ บอทได้ทำการแบนออกเรียบร้อย")
                    except Exception:
                        pass
    except Exception:
        pass

# 3. ป้องกันสแปมข้อความ & อีโมจิรัวๆ (แก้ใขปัญหาลูปเตือนซ้ำๆ)
@bot.event
async def on_message(message):
    # ถ้าผู้ส่งเป็นบอท หรือไม่ใช่กิลด์ (เช่น DM) ให้ข้ามทันที
    if message.author.bot or not message.guild:
        return

    # ถ้าแอดมินพิมพ์ ให้ข้ามระบบสแปม
    if message.author.guild_permissions.administrator:
        await bot.process_commands(message)
        return

    user_id = message.author.id
    guild = message.guild
    now = datetime.datetime.now()

    spam_tracker[user_id].append(now)
    while spam_tracker[user_id] and (now - spam_tracker[user_id][0]).total_seconds() > 5:
        spam_tracker[user_id].popleft()

    # นับจำนวนอีโมจิในข้อความ
    emoji_count = message.content.count('<:') + message.content.count('<a:')
    
    # ถ้าพิมพ์รัวเกิน 5 ข้อความใน 5 วิ หรือส่งอีโมจิรัวเกิน 10 ตัว
    if len(spam_tracker[user_id]) > 5 or emoji_count > 10:
        try:
            # 1. ลบข้อความปัจจุบันที่กำลังส่งเข้ามา
            await message.delete()

            # 2. ค้นหาและลบข้อความของ User คนนี้ในช่วง 10 วินาทีที่ผ่านมา
            ten_seconds_ago = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(seconds=10)
            async for history_msg in message.channel.history(limit=25, after=ten_seconds_ago):
                if history_msg.author.id == user_id:
                    try:
                        await history_msg.delete()
                    except:
                        pass

            # 3. สั่ง Timeout สมาชิกคนนั้นเป็นเวลา 15 วินาที
            member = guild.get_member(user_id)
            if member:
                timeout_duration = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=15)
                await member.timeout(timeout_duration, reason="Anti-Spam: สแปมข้อความหรืออีโมจิรัวๆ")

            # 4. ส่งแจ้งเตือนเข้าห้อง บอท-log (ส่งแค่ครั้งเดียวต่อการสแปม 1 รอบ)
            await send_security_log(
                guild, 
                "ตรวจพบการสแปมข้อความ/อีโมจิ!", 
                f"ผู้ใช้ `{message.author}` ทำการสแปมในห้อง {message.channel.mention}\nบอทได้ทำการลบข้อความย้อนหลังและ **Timeout 15 วินาที** เรียบร้อย"
            )

            # 5. เคลียร์ค่า spam_tracker เพื่อไม่ให้ติดลูปซ้ำ
            spam_tracker[user_id].clear()

            # 6. แจ้งเตือนหน้าแชท (ลบอัตโนมัติใน 3 วิ)
            warning = await message.channel.send(f"{message.author.mention} ⚠️ **กรุณาอย่าสแปมข้อความหรืออีโมจิรัวๆ! (ถูกห้ามพิมพ์ 15 วินาที)**")
            await asyncio_sleep_delete(warning)
            return
        except Exception:
            pass

    await bot.process_commands(message)

async def asyncio_sleep_delete(msg):
    import asyncio
    await asyncio.sleep(3)
    try:
        await msg.delete()
    except:
        pass




# --- คำสั่งรีสตาร์ทบอท ---
@bot.command(name="restart")
async def restart_bot(ctx):
    if ctx.author.id == ctx.guild.owner_id:
        await ctx.send("🔄 กำลังรีสตาร์ทบอท, กรุณารอสักครู่...")
        await bot.close()
        os._exit(0)
    else:
        await ctx.send("❌ คุณไม่มีสิทธิ์ใช้คำสั่งนี้จ้า!")

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    try:
        await bot.sync_all_application_commands()
        print("Successfully synced application commands.")
    except Exception as e:
        print(f"Failed to sync commands: {e}")



# ==========================================
# 🌸 ส่วนระบบเซฟยศ (SaveroleView)
# ==========================================
class SaveroleView(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.cooldowns = {}

    @button(label="เซฟยศ", style=1, emoji="🍓")
    async def save(self, button: nextcord.ui.Button, interaction: Interaction):
        user = interaction.user
        if user.id in self.cooldowns and datetime.datetime.now() < self.cooldowns[user.id]:
            cooldown_end = self.cooldowns[user.id]
            remaining_time = (cooldown_end - datetime.datetime.now()).total_seconds()
            hours, remainder = divmod(int(remaining_time), 3600)
            minutes, seconds = divmod(remainder, 60)
            embed = Embed(
                title="⏰ Cooldown",
                description=f"โปรดรอ {hours} ชั่วโมง {minutes} นาที ก่อนที่จะเซฟยศอีกครั้งนะจ๊ะ",
                color=COLOR
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        self.cooldowns[user.id] = datetime.datetime.now() + datetime.timedelta(days=1)
        
        os.makedirs("data", exist_ok=True)
        role_data = [role.name for role in user.roles if role.name != "@everyone"]
        
        file_path = f"data/role_{user.id}.json" 
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(role_data, f)

        embed = Embed(title="💖 บันทึกสำเร็จ!", description="ยศของคุณถูกบันทึกไว้ในระบบเรียบร้อยแล้วจ้า 🎉", color=COLOR)
        formatted_roles = ", ".join(role_data) if role_data else "ไม่มียศ"
        embed.add_field(name="🌸 ยศที่บันทึก", value=f"`{formatted_roles}`", inline=False)
        embed.set_thumbnail(url=user.avatar.url if user.avatar else user.default_avatar.url)
        embed.set_footer(text=f"Powered by {hosting_name}")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @button(label="รับยศคืน", style=1, emoji="🍡")
    async def get(self, button: nextcord.ui.Button, interaction: Interaction):
        user = interaction.user
        file_path = f"data/role_{user.id}.json" 
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                role_data = json.load(f)
                formatted_roles = [role for role in role_data]
                for role_name in role_data:
                    roles = nextcord.utils.get(interaction.guild.roles, name=role_name)
                    
                    if roles:
                        if roles.position > interaction.guild.me.top_role.position:
                            embed = Embed(
                                title="⚠️ ไม่สามารถเพิ่มยศได้",
                                description=f"ฉันไม่สามารถเพิ่มยศ {roles.mention} ได้เพราะตำแหน่งสูงกว่ายศสูงสุดของฉัน",
                                color=COLOR
                            )
                            await interaction.response.send_message(embed=embed, ephemeral=True)
                            return
                        await user.add_roles(roles)
                    else:
                        embed = Embed(
                            title="❌ ไม่พบยศนี้",
                            description=f"ยศ `{role_name}` ไม่มีอยู่ในเซิร์ฟเวอร์นี้แล้ว",
                            color=COLOR
                        )
                        await interaction.response.send_message(embed=embed, ephemeral=True)
        except FileNotFoundError:
            await interaction.response.send_message(embed=Embed(
                description="**🌸 คุณยังไม่ได้บันทึกยศของคุณเลยนะ!**",
                color=COLOR
            ), ephemeral=True)
            return

        description = "**🍡 ยศของคุณได้ถูกคืนเรียบร้อยแล้วจ้า!**"
        if formatted_roles:
            description += "\n\n**🌸 ยศที่ได้รับคืน:**\n"
            for role in formatted_roles:
                description += f"- ```{role}```\n"

        await interaction.response.send_message(embed=Embed(
            description=description,
            color=COLOR 
        ), ephemeral=True)

    @button(label="ดูข้อมูลผู้ใช้", style=1, emoji="🍰")
    async def get_user_info(self, button: nextcord.ui.Button, interaction: Interaction):
        user = interaction.user
        created_since = (interaction.message.created_at - user.created_at).days
        created_since_str = f"{created_since} วันที่ผ่านมา"

        user_info_embed = nextcord.Embed(title=f"🌸 ข้อมูลของ {user.display_name}", color=COLOR)
        if user.avatar:
            user_info_embed.set_thumbnail(url=user.avatar.url)

        user_info_embed.add_field(name="🆔 Discord ID", value=user.id, inline=False)
        user_info_embed.add_field(name="📅 วันที่สร้างบัญชี", value=created_since_str, inline=False)

        if len(user.roles) > 1:
            roles = ", ".join([role.mention for role in user.roles[1:]])
            user_info_embed.add_field(name="👑 ยศ", value=roles, inline=False)

        if user.premium_since:
            user_info_embed.add_field(name="✨ Nitro Boost", value="สนับสนุนตั้งแต่: " + user.premium_since.strftime("%Y-%m-%d"), inline=False)

        await interaction.response.send_message(content="🍰 นี่คือข้อมูลผู้ใช้ของคุณจ้า:", embed=user_info_embed, ephemeral=True)

    @nextcord.ui.button(label="คนเซฟยศ", style=1, emoji="🎀")
    async def check_saved_roles(self, button: nextcord.Button, interaction: nextcord.Interaction):
        folder_path = "data"
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        files = os.listdir(folder_path)
        saved_roles_count = len(files)

        embed = nextcord.Embed(
            title=f"🌸 จำนวนผู้เซฟยศทั้งหมด",
            description=f"มีคนบันทึกยศทั้งหมด: `{saved_roles_count}` คน",
            color=COLOR
        )
        if saved_roles_count > 0:
            embed.add_field(
                name=f"📋 รายชื่อผู้ที่เซฟยศ",
                value="\n".join([f"- {filename.replace('role_', '<@').replace('.json', '>')}" for filename in files]),
                inline=False
            )
        else:
            embed.add_field(
                name="📋 รายชื่อผู้ที่เซฟยศ",
                value="ยังไม่มีใครบันทึกยศในขณะนี้เลย",
                inline=False
            )

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @nextcord.ui.button(label="ดูประวัติยศ", style=1, emoji="📖")
    async def role_history(self, button: nextcord.Button, interaction: nextcord.Interaction):
        user = interaction.user
        file_path = f"data/role_{user.id}.json"
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                role_data = json.load(f)
                roles_formatted = "\n".join([f"```- {role}```" for role in role_data]) if role_data else "ไม่มีประวัติยศ"
                
                embed = nextcord.Embed(
                    title="📖 ประวัติยศที่คุณบันทึกไว้", 
                    description=roles_formatted,
                    color=COLOR 
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
        except FileNotFoundError:
            embed = nextcord.Embed(
                title="⚠️ เกิดข้อผิดพลาด",
                description="คุณยังไม่ได้บันทึกยศของคุณเลยนะ",
                color=nextcord.Color.pink()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @nextcord.ui.button(label="เช็คยศตัวเอง", style=1, emoji="🔍")
    async def check_my_roles(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        member_roles = [f"> 🌸 {role.mention} (ID : `{role.id}`)" for role in interaction.user.roles if role.name != '@everyone' and not role.managed]
        num_roles = len(member_roles)

        if not member_roles:
            embed = nextcord.Embed(
                title="🌸 แจ้งเตือน", 
                description="**คุณยังไม่มีบทบาท/ยศใดๆ ในขณะนี้จ้า**", 
                color=COLOR
            )
        else:
            embed = nextcord.Embed(
                title="🍡 ยศทั้งหมดของคุณมีดังนี้:", 
                description="\n".join(member_roles),
                color=COLOR
            )
            embed.set_thumbnail(url=interaction.user.display_avatar.url)
            embed.add_field(name="✨ ตรวจสอบเรียบร้อย!", value=f"**มีจำนวนยศทั้งหมด {str(num_roles)} ยศ**", inline=False)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @button(label="วิธีการใช้งาน", style=2, emoji="💌")
    async def usage(self, button: nextcord.ui.Button, interaction: Interaction):
        instructions = "```🌸 วิธีการใช้งานระบบเซฟยศ 🌸\n1. กดปุ่ม 'เซฟยศ' (🍓) เพื่อบันทึกยศของคุณ\n2. กดปุ่ม 'รับยศคืน' (🍡) เพื่อเรียกคืนยศเดิม```"
        embed = Embed(title="💌 คำแนะนำการใช้งาน", description=instructions, color=COLOR)
        embed.set_footer(text=f"Made with love by {owner_user}!")
        await interaction.response.send_message(embed=embed, ephemeral=True)


# ==========================================
# 📝 ส่วนระบบตอบคำถามรับยศ
# ==========================================
class MathVerifyModal(Modal):
    def __init__(self, num1, num2, correct_answer):
        super().__init__(title="🌸 ยืนยันตัวตนรับยศ (Waguri)")
        self.correct_answer = correct_answer

        self.answer_input = TextInput(
            label=f"จงหาผลลัพธ์: {num1} + {num2} = ?",
            placeholder="พิมพ์ตัวเลขคำตอบลงที่นี่...",
            min_length=1,
            max_length=5,
            required=True
        )
        self.add_item(self.answer_input)

    async def callback(self, interaction: Interaction):
        user_input = self.answer_input.value.strip()
        
        try:
            user_num = int(user_input)
        except ValueError:
            return await interaction.response.send_message(content="❌ กรุณากรอกเป็นตัวเลขเท่านั้นนะจ๊ะ!", ephemeral=True)

        if user_num == self.correct_answer:
            role_name_to_give = "Member"  
            role = nextcord.utils.get(interaction.guild.roles, name=role_name_to_give)

            if not role:
                return await interaction.response.send_message(content=f"⚠️ ไม่พบยศ `{role_name_to_give}` ในเซิร์ฟเวอร์นี้ กรุณาสร้างยศชื่อนี้ก่อนจ้า!", ephemeral=True)

            try:
                await interaction.user.add_roles(role)
                embed = Embed(title="🎉 ยืนยันตัวตนสำเร็จ!", description=f"คุณตอบคำถามถูกต้องและได้รับยศ **{role.name}** เรียบร้อยแล้วจ้า 🌸", color=COLOR)
                await interaction.response.send_message(embed=embed, ephemeral=True)
            except Exception as e:
                await interaction.response.send_message(content=f"❌ เกิดข้อผิดพลาดในการเพิ่มยศ: โปรดตรวจสอบว่ายศของบอทอยู่สูงกว่ายศ `{role_name_to_give}` หรือไม่", ephemeral=True)
        else:
            embed = Embed(title="❌ ตอบผิดจ้า!", description=f"เสียใจด้วยนะ คำตอบที่คุณกรอกไม่ถูกต้อง ลองกดปุ่มทำใหม่อีกครั้งได้เลย 🍡", color=COLOR)
            await interaction.response.send_message(embed=embed, ephemeral=True)

class VerifyView(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @button(label="ตอบคำถามรับยศ", style=3, emoji="📝")
    async def verify_math(self, button: nextcord.ui.Button, interaction: Interaction):
        num1 = random.randint(10, 99)
        num2 = random.randint(1, 99)
        correct_answer = num1 + num2
        await interaction.response.send_modal(MathVerifyModal(num1, num2, correct_answer))


# ==========================================
# 🚀 คำสั่ง Slash Commands
# ==========================================

@bot.slash_command(name="saverole_menu", description="ส่งเมนูระบบบันทึกและจัดการยศ")
async def saverole_setup(interaction: nextcord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message(content='[ERROR] No Permission For Use This Command.', ephemeral=True)

    # ลบคำว่า - Waguri Theme ออกแล้ว
    embed = nextcord.Embed(
        title="🌸 **ระบบบันทึกยศ** 🍡",
        description="``` > เซฟยศ (บันทึกยศของคุณไว้ในระบบ)\n > รับยศคืน (เรียกคืนยศเดิมของคุณ)```",
        color=COLOR
    )
    embed.set_image(url=Animated_Image)
    
    if bot.user.avatar:
        embed.set_footer(text=f"Powered by {hosting_name}", icon_url=bot.user.avatar.url)
        embed.set_author(name="แหนม", icon_url=bot.user.avatar.url) # เปลี่ยนชื่อเป็น แหนม แล้ว
    else:
        embed.set_footer(text=f"Powered by {hosting_name}")
        embed.set_author(name="แหนม")

    await interaction.channel.send(embed=embed, view=SaveroleView())
    await interaction.response.send_message(content='[SUCCESS] ส่งเมนูเซฟยศเรียบร้อย!', ephemeral=True)


@bot.slash_command(name="verify_menu", description="ส่งเมนูกดรับยศผ่านการตอบคำถามสุ่มเลข")
async def verify_menu(interaction: nextcord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message(content='[ERROR] No Permission For Use This Command.', ephemeral=True)

    guild = interaction.guild
    embed = nextcord.Embed(
        title="🌸 **ระบบยืนยันตัวตนตอบคำถามรับยศ** 🍡",
        description="``` > กดปุ่มด้านล่างเพื่อตอบคำถามบวกเลข\n > หากตอบถูกจะได้รับยศทันที!```",
        color=COLOR
    )
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
    
    if bot.user.avatar:
        embed.set_footer(text=f"Powered by {hosting_name}", icon_url=bot.user.avatar.url)
        embed.set_author(name="แหนม", icon_url=bot.user.avatar.url) # เปลี่ยนชื่อเป็น แหนม แล้ว
    else:
        embed.set_footer(text=f"Powered by {hosting_name}")
        embed.set_author(name="แหนม")

    await interaction.channel.send(embed=embed, view=VerifyView())
    await interaction.response.send_message(content='[SUCCESS] ส่งเมนูยืนยันตัวตนเรียบร้อย!', ephemeral=True)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    try:
        await bot.sync_all_application_commands()
        print("Successfully synced application commands.")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

bot.run(TOKEN)
