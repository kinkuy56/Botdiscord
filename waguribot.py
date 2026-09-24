ลิงก์ภาพเคลื่อนไหวเมนูเซฟยศN flask import Flask
from threading import Thread
import os

app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# เรียกใช้งานฟังก์ชันเปิดเว็บจำลอง
keep_alive()

import discord
from discord.ext import commands
import asyncio

import discord
from discord.interactions import Interaction
import requests
import random
import json
import asyncio
import os
from discord.ui import Button, View, Modal
from discord import app_commands, ui

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
token = os.getenv('DISCORD_TOKEN')

owner_user = "jarya_dang"
COLOR = 0xffb6c1  # สีชมพูอ่อนพาสเทลเข้ากับ Waguri
hosting_name = 'แหนม'



# 🎞️ ลิงก์ภาพเคลื่อนไหวเมนูเซฟยศ
Animated_Image = 'https://cdn.discordapp.com/attachments/1168170116383522817/1552008477432356874/kaoruko-waguri-waguri-kaoruko.gif?ex=6ab40c07&is=6ab2ba87&hm=523ce1235101c280bd85f9136400e28ff3f815b04b6ba82b706023269fcf70ec&'
# สมมติว่าใน waguribot.py ของคุณมีตัวแปร bot อยู่แล้ว เช่น:
# bot = commands.Bot(command_prefix="!", intents=intents)


# สร้างโฟลเดอร์ casino_data อัตโนมัติหากยังไม่มี
os.makedirs("casino_data", exist_ok=True)

# โหลดข้อมูลจาก config.json
with open("config.json", "r", encoding="utf-8") as file:
    config = json.load(file)

admin_name = config.get('admin_name', 'jarya_dang')
server_id = int(config.get('server_id', 0))

MYGUILD = discord.Object(id=server_id)

class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        self.tree.copy_global_to(guild=MYGUILD)
        await self.tree.sync(guild=MYGUILD)

intents = discord.Intents.default()
client = MyClient(intents=intents)

class shopping_discord(discord.ui.Modal, title="วางเดิมพัน"):
    num = discord.ui.TextInput(
        label="NUMBER", 
        placeholder=f"กรอกหมายเลข 1 - {config.get('bet', 5)}", 
        required=True, 
        max_length=2, 
        style=discord.TextStyle.short
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        user = interaction.user
        file_path = f"casino_data/{user.name}.json"
        
        try:
            val = int(self.num.value)
            bet_limit = int(config.get('bet', 5))
            
            if val > bet_limit or val < 1:
                embed = discord.Embed(title="❌ ไม่สามารถเดิมพันได้", description=f"กรุณากรอกหมายเลขระหว่าง 1 - {bet_limit}", color=0xFCE5CD)
                await interaction.followup.send(embed=embed, ephemeral=True)
                return

            result = random.randint(1, bet_limit)
            log_channel = discord.utils.get(interaction.guild.channels, id=int(config.get('log', 0)))
            
            # โหลดเงินปัจจุบัน
            balance = 0.0
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    balance = float(data.get(user.name, {}).get('amount', 0.0))

            if val == result:
                reward = float(config.get('reward', 10))
                newtotal = balance + reward
                
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump({user.name: {"id": str(user.id), "amount": newtotal}}, f, indent=4)
                    
                embed = discord.Embed(title="✅ ยินดีด้วยคุณได้รับรางวัล", description=f"หมายเลขที่ออกคือ : {result} || ได้รับเงินรางวัลรวม {reward:.2f} บาท !!", color=0xFCE5CD)
                await interaction.followup.send(embed=embed, ephemeral=True)
                
                if log_channel:
                    embeds = discord.Embed(title=f"✅ <@{user.id}> ได้รับรางวัล!", description=f"ทายเลข: {val}\nชนะและได้รับรางวัลรวม {reward:.2f} บาท", color=0xFCE5CD)
                    embeds.set_footer(text=f"ยอดเงินคงเหลือ : {newtotal:.2f} บาท")
                    await log_channel.send(embed=embeds)
            else:
                deduct = float(config.get('deduct', 5))
                newtotal = max(0.0, balance - deduct)
                
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump({user.name: {"id": str(user.id), "amount": newtotal}}, f, indent=4)
                    
                embed = discord.Embed(title="❌ คุณไม่ได้รับรางวัล", description=f"เนื่องจากหมายเลขที่ออกคือ : {result} || ขอแสดงความเสียใจ!", color=0xFCE5CD)
                await interaction.followup.send(embed=embed, ephemeral=True)
                
                if log_channel:
                    embeds = discord.Embed(title=f"❌ <@{user.id}> ไม่ได้รับรางวัล!", description=f"ทายเลข: {val} เลขที่ออก: {result}\nแพ้และเสียเงินจำนวน -{deduct:.2f} บาท", color=0xFCE5CD)
                    embeds.set_footer(text=f"ยอดเงินคงเหลือ : {newtotal:.2f} บาท")
                    await log_channel.send(embed=embeds)

        except Exception as e:
            embed = discord.Embed(title="❌ เกิดข้อผิดพลาด", description="รูปแบบข้อมูลไม่ถูกต้อง กรุณาลองใหม่อีกครั้ง", color=0xFCE5CD)
            await interaction.followup.send(embed=embed, ephemeral=True)

class topup(discord.ui.Modal, title="เติมเงินเข้ากระเป๋า"):
    link_angpao = discord.ui.TextInput(label="เติมเงินเข้ากระเป๋าสำหรับเดิมพัน", placeholder="ลิ้งค์อั่งเปาของคุณ 💸 | URL", required=True, max_length=100, style=discord.TextStyle.short)
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        user = interaction.user
        try:
            response = requests.post(
                "https://restapi.kdkddmdmdd.repl.co/undefined_store/topupwallet", 
                json={"mobile": str(config.get('phone')), "link": str(self.link_angpao.value)}
            ).json()
            
            if response.get("status") == True:
                money_amount = float(response["amount"])
                file_path = f"casino_data/{user.name}.json"
                
                amount = 0.0
                if os.path.exists(file_path):
                    with open(file_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        amount = float(data.get(user.name, {}).get('amount', 0.0))
                
                newamount = amount + money_amount
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump({user.name: {"id": str(user.id), "amount": newamount}}, f, indent=4)
                    
                embed = discord.Embed(title="✅ เติมเงินเข้ากระเป๋าสำเร็จ", description=f"เติมเงินเข้ากระเป๋าเรียบร้อยแล้วจำนวนเงิน {money_amount:.2f} บาท", color=0xFCE5CD)
                await interaction.followup.send(embed=embed, ephemeral=True)
                
                log_channel = discord.utils.get(interaction.guild.channels, id=int(config.get('log', 0)))
                if log_channel:
                    embeds = discord.Embed(title=f"✅ <@{user.id}> เติมเงินสำเร็จ!", description=f"เติมเงินสำเร็จแล้วจำนวน: {money_amount:.2f} บาท", color=0xFCE5CD)
                    await log_channel.send(embed=embeds)
            elif response.get("reason") == "VOUCHER_NOT_FOUND":
                embed = discord.Embed(title="❌ เติมเงินไม่สำเร็จ", description="ซองอั่งเปานี้ไม่มีอยู่กรุณาลองใหม่อีกครั้ง !", color=0xFCE5CD)
                await interaction.followup.send(embed=embed, ephemeral=True)
            else:
                embed = discord.Embed(title="❌ เติมเงินไม่สำเร็จ", description="เนื่องจากซองอั่งเปานี้ได้รับเงินไปแล้ว !", color=0xFCE5CD)
                await interaction.followup.send(embed=embed, ephemeral=True)
        except Exception as e:
            embed = discord.Embed(title="❌ เกิดข้อผิดพลาด", description="ไม่สามารถเชื่อมต่อกับระบบเติมเงินได้", color=0xFCE5CD)
            await interaction.followup.send(embed=embed, ephemeral=True)

class getmoney(discord.ui.Modal, title="ถอนเงิน"):
    phone1 = discord.ui.TextInput(label="ทรูมันนี่วอเล็ต", placeholder="เบอร์", required=True, max_length=10, style=discord.TextStyle.short)
    withdraw1 = discord.ui.TextInput(label=f"ถอนเงิน (ขั้นต่ำ {config.get('withdraw', 30)} บาท)", placeholder="จำนวนการถอนเงิน", required=True, max_length=10, style=discord.TextStyle.short)
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        user = interaction.user
        file_path = f"casino_data/{user.name}.json"
        
        try:
            req_amount = float(self.withdraw1.value)
            min_withdraw = float(config.get('withdraw', 30))
            
            if req_amount < min_withdraw:
                embed = discord.Embed(title="❌ ไม่สามารถทำรายการถอนเงินได้", description=f"ขั้นต่ำการถอนเงินคือ {min_withdraw:.2f} บาท !!", color=0xFCE5CD)
                await interaction.followup.send(embed=embed, ephemeral=True)
                return

            if not os.path.exists(file_path):
                embed = discord.Embed(title="❌ ไม่พบเครดิตของคุณ", description="กรุณาเปิดบัญชีหรือเติมเงินก่อนใช้งาน", color=0xFCE5CD)
                await interaction.followup.send(embed=embed, ephemeral=True)
                return

            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                balance = float(data.get(user.name, {}).get('amount', 0.0))

            if req_amount > balance:
                embed = discord.Embed(title="❌ ไม่สามารถทำรายการถอนเงินได้", description=f"ยอดเงินคงเหลือไม่เพียงพอ (ยอดเงินคงเหลือ: {balance:.2f} บาท)", color=0xFCE5CD)
                await interaction.followup.send(embed=embed, ephemeral=True)
            else:
                low = balance - req_amount
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump({user.name: {"id": str(user.id), "amount": low}}, f, indent=4)
                    
                embed = discord.Embed(title="✅ เพิ่มรายการถอนเงินแล้ว", description=f"รายการถอนเงินจำนวน : {req_amount:.2f} บาท ถอนเข้าเบอร์วอเล็ต : {self.phone1.value}", color=0xFCE5CD)
                await interaction.followup.send(embed=embed, ephemeral=True)
                
                log_channel = discord.utils.get(interaction.guild.channels, id=int(config.get('log', 0)))
                if log_channel:
                    embedlog = discord.Embed(title=f"✅ <@{user.id}> ถอนเงิน", description=f"ผู้ใช้ <@{user.id}> ได้ทำการขอถอนเงินจำนวน **{req_amount:.2f} บาท** เบอร์ **{self.phone1.value}**", color=0xFCE5CD)
                    await log_channel.send(embed=embedlog)
        except Exception as e:
            embed = discord.Embed(title="❌ ไม่สามารถถอนเงินได้", description="รูปแบบการถอนเงินไม่ถูกต้อง กรุณาลองใหม่อีกครั้ง!", color=0xFCE5CD)
            await interaction.followup.send(embed=embed, ephemeral=True)

class transfer(discord.ui.Modal, title="โอนเงิน"):
    name = discord.ui.TextInput(label="ชื่อบัญชีผู้รับเงิน", placeholder="กรอกชื่อคนที่จะโอนให้", required=True, max_length=40, style=discord.TextStyle.short)
    count = discord.ui.TextInput(label="จำนวนเงิน", placeholder="กรอกจำนวนเงินที่ต้องการโอน", required=True, max_length=10, style=discord.TextStyle.short)
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        user = interaction.user
        sender_file = f"casino_data/{user.name}.json"
        receiver_file = f"casino_data/{self.name.value}.json"
        
        try:
            transfer_amount = float(self.count.value)
            if not os.path.exists(receiver_file):
                embed = discord.Embed(title="❌ ไม่สามารถโอนเงินได้", description=f"ไม่พบบัญชี {self.name.value} ในระบบ!", color=0xFCE5CD)
                await interaction.followup.send(embed=embed, ephemeral=True)
                return

            if not os.path.exists(sender_file):
                embed = discord.Embed(title="❌ ไม่สามารถโอนเงินได้", description="ไม่พบเครดิตของคุณ กรุณาเติมเงินก่อนโอน!", color=0xFCE5CD)
                await interaction.followup.send(embed=embed, ephemeral=True)
                return

            with open(sender_file, "r", encoding="utf-8") as f:
                sender_data = json.load(f)
                sender_balance = float(sender_data.get(user.name, {}).get('amount', 0.0))

            if sender_balance < transfer_amount:
                embed = discord.Embed(title="❌ ไม่สามารถโอนเงินได้", description="ยอดเงินคงเหลือไม่เพียงพอ!", color=0xFCE5CD)
                embed.set_footer(text=f"ยอดเงินคงเหลือ : {sender_balance:.2f} บาท")
                await interaction.followup.send(embed=embed, ephemeral=True)
            else:
                new_sender_balance = sender_balance - transfer_amount
                with open(sender_file, "w", encoding="utf-8") as f:
                    json.dump({user.name: {"id": str(user.id), "amount": new_sender_balance}}, f, indent=4)

                with open(receiver_file, "r", encoding="utf-8") as f:
                    rec_data = json.load(f)
                    rec_balance = float(rec_data.get(self.name.value, {}).get('amount', 0.0))
                    rec_id = rec_data.get(self.name.value, {}).get('id', '')

                new_rec_balance = rec_balance + transfer_amount
                with open(receiver_file, "w", encoding="utf-8") as f:
                    json.dump({self.name.value: {"id": rec_id, "amount": new_rec_balance}}, f, indent=4)

                embed = discord.Embed(title="✅ โอนเงินสำเร็จแล้ว !", description=f"จาก: {user.name}\nโอนไปยัง: {self.name.value}\nจำนวนเงิน: {transfer_amount:.2f} บาท", color=0xFCE5CD)
                embed.set_footer(text=f"ยอดเงินคงเหลือ : {new_sender_balance:.2f} บาท")
                await interaction.followup.send(embed=embed, ephemeral=True)

                log_channel = discord.utils.get(interaction.guild.channels, id=int(config.get('log', 0)))
                if log_channel:
                    embeds = discord.Embed(title=f"<@{user.id}> โอนเงินสำเร็จ", description=f"โอนไปยัง: {self.name.value}\nจำนวนเงิน: {transfer_amount:.2f} บาท", color=0xFCE5CD)
                    await log_channel.send(embed=embeds)
        except Exception as e:
            embed = discord.Embed(title="❌ ไม่สามารถโอนเงินได้", description="รูปแบบข้อมูลไม่ถูกต้อง กรุณาลองใหม่อีกครั้ง!", color=0xFCE5CD)
            await interaction.followup.send(embed=embed, ephemeral=True)

class CasinoButtons(View):
    def __init__(self):
        super().__init__(timeout=None)

class CasinoButtons(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="เริ่มเดิมพัน", style=discord.ButtonStyle.green, emoji="💎", custom_id="btn_bet")
    async def btn_bet_cb(self, interaction: discord.Interaction, button: Button):
        if interaction.response.is_done():
            return
        user = interaction.user
        file_path = f"casino_data/{user.name}.json"
        if not os.path.exists(file_path):
            embed = discord.Embed(title="❌ ไม่สามารถเดิมพันได้", description="ไม่พบเครดิตของคุณ กรุณาเปิดบัญชีหรือเติมเงินก่อนเดิมพัน!", color=0xFCE5CD)
            try:
                await interaction.response.send_message(embed=embed, ephemeral=True)
            except discord.NotFound:
                pass
            return

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            balance = float(data.get(user.name, {}).get('amount', 0.0))

        deduct_limit = int(config.get('deduct', 5))
        if balance < deduct_limit:
            embed = discord.Embed(title="❌ ไม่สามารถเดิมพันได้", description=f"ยอดเงินคงเหลือไม่เพียงพอ กรุณาเติมเงินเข้ากระเป๋าขั้นต่ำ {deduct_limit} บาท ขึ้นไป", color=0xFCE5CD)
            try:
                await interaction.response.send_message(embed=embed, ephemeral=True)
            except discord.NotFound:
                pass
        else:
            try:
                await interaction.response.send_modal(shopping_discord())
            except discord.NotFound:
                pass

    @discord.ui.button(label="เติมเงินเข้ากระเป๋า", style=discord.ButtonStyle.green, emoji="💰", custom_id="btn_topup")
    async def btn_topup_cb(self, interaction: discord.Interaction, button: Button):
        if interaction.response.is_done():
            return
        try:
            await interaction.response.send_modal(topup())
        except discord.NotFound:
            pass

    @discord.ui.button(label="เช็คยอดเงิน", style=discord.ButtonStyle.green, emoji="💳", custom_id="btn_balance")
    async def btn_balance_cb(self, interaction: discord.Interaction, button: Button):
        if interaction.response.is_done():
            return
        user = interaction.user
        file_path = f"casino_data/{user.name}.json"
        try:
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    balance = float(data.get(user.name, {}).get('amount', 0.0))
                embed = discord.Embed(title="กระเป๋าตังค์ของคุณ", description=f"ยอดเงินคงเหลือ : {balance:.2f} บาท", color=0xFCE5CD)
                await interaction.response.send_message(embed=embed, ephemeral=True)
            else:
                embed = discord.Embed(title="❌ ไม่พบเครดิตของคุณ", description=f"**name : {user.name}\nuid : {user.id}**\nไม่พบเครดิตของคุณ กรุณาเปิดบัญชี/เติมเงินก่อนเดิมพัน!", color=0xFCE5CD)
                await interaction.response.send_message(embed=embed, ephemeral=True)
        except discord.NotFound:
            pass

    @discord.ui.button(label="ถอนเงิน", style=discord.ButtonStyle.green, emoji="💸", custom_id="btn_withdraw")
    async def btn_withdraw_cb(self, interaction: discord.Interaction, button: Button):
        if interaction.response.is_done():
            return
        user = interaction.user
        file_path = f"casino_data/{user.name}.json"
        try:
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    balance = float(data.get(user.name, {}).get('amount', 0.0))
                min_withdraw = float(config.get('withdraw', 30))
                if balance < min_withdraw:
                    embed = discord.Embed(title="❌ ไม่สามารถถอนเงินได้", description=f"ยอดเงินของคุณไม่เพียงพอสำหรับการถอนเงิน (ขั้นต่ำ {min_withdraw:.2f} บาท)", color=0xFCE5CD)
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                else:
                    await interaction.response.send_modal(getmoney())
            else:
                embed = discord.Embed(title="❌ ไม่สามารถถอนเงินได้", description="ไม่พบเครดิตของคุณกรุณาเติมเงินก่อนถอนเงิน !", color=0xFCE5CD)
                await interaction.response.send_message(embed=embed, ephemeral=True)
        except discord.NotFound:
            pass

    @discord.ui.button(label="เปิดบัญชี", style=discord.ButtonStyle.green, emoji="📝", custom_id="btn_open_acc")
    async def btn_open_cb(self, interaction: discord.Interaction, button: Button):
        if interaction.response.is_done():
            return
        user = interaction.user
        file_path = f"casino_data/{user.name}.json"
        try:
            if os.path.exists(file_path):
                embed = discord.Embed(title="❌ ไม่สามารถเปิดบัญชีได้", description="เนื่องจากคุณมีบัญชีอยู่แล้ว กรุณาเติมเงินเข้ากระเป๋าเพื่อเดิมพัน !", color=0xFCE5CD)
                await interaction.response.send_message(embed=embed, ephemeral=True)
            else:
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump({user.name: {"id": str(user.id), "amount": 0.0}}, f, indent=4)
                embed = discord.Embed(title="✅ เปิดบัญชีสำเร็จแล้ว !", description=f"**เปิดบัญชีสำเร็จ**\nuid : {user.id}\nname : {user.name}\nยอดเงินคงเหลือ : 0.00 บาท", color=0xFCE5CD)
                await interaction.response.send_message(embed=embed, ephemeral=True)
        except discord.NotFound:
            pass

    @discord.ui.button(label="โอนเงิน", style=discord.ButtonStyle.green, emoji="🔄", custom_id="btn_transfer")
    async def btn_transfer_cb(self, interaction: discord.Interaction, button: Button):
        if interaction.response.is_done():
            return
        user = interaction.user
        file_path = f"casino_data/{user.name}.json"
        try:
            if os.path.exists(file_path):
                await interaction.response.send_modal(transfer())
            else:
                embed = discord.Embed(title="❌ ไม่สามารถโอนเงินได้", description="ไม่พบเครดิตของคุณกรุณาเติมเงินก่อนโอนเงิน !", color=0xFCE5CD)
                await interaction.response.send_message(embed=embed, ephemeral=True)
        except discord.NotFound:
            pass
            
    print(f'We have logged in as {clien

# ---------------------------------------------------------
# 1. โค้ดส่วนระบบ Ticket
# ---------------------------------------------------------
class CloseView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔒 ปิด Ticket", style=discord.ButtonStyle.danger, custom_id="close_ticket_btn")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("กำลังปิดห้องนี้ใน 5 วินาที...", ephemeral=False)
        await asyncio.sleep(5)
        try:
            await interaction.channel.delete()
        except Exception as e:
            print(f"เกิดข้อผิดพลาดในการลบห้อง: {e}")

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🎫 เปิด Ticket", style=discord.ButtonStyle.primary, custom_id="open_ticket_btn")
    async def create_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        member = interaction.user

        existing_channel = discord.utils.get(guild.text_channels, name=f"ticket-{member.name.lower()}")
        if existing_channel:
            await interaction.response.send_message(f"คุณมีห้อง Ticket เปิดอยู่แล้ว: {existing_channel.mention}", ephemeral=True)
            return

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            member: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, manage_channels=True)
        }

        category = interaction.channel.category
        ticket_channel = await guild.create_text_channel(
            name=f"ticket-{member.name}",
            category=category,
            overwrites=overwrites,
            topic=f"Ticket ของ {member.id}"
        )

        embed = discord.Embed(
            title="support ticket",
            description=f"สวัสดีคุณ {member.mention} ทีมงานจะเข้ามาช่วยเหลือโดยเร็วที่สุด\nกรุณาพิมพ์แจ้งปัญหาของคุณไว้ได้เลยครับ",
            color=discord.Color.green()
        )
        await ticket_channel.send(embed=embed, view=CloseView())
        await interaction.response.send_message(f"สร้างห้อง Ticket ให้คุณแล้วครับ: {ticket_channel.mention}", ephemeral=True)

@bot.command(name="setup_ticket")
@commands.has_permissions(administrator=True)
async def setup_ticket(ctx):
    embed = discord.Embed(
        title="ระบบแจ้งปัญหา / ติดต่อทีมงาน (Support Ticket)",
        description="กดปุ่มด้านล่างนี้เพื่อเปิดห้องพูดคุยกับทีมงานส่วนตัวครับ",
        color=discord.Color.blue()
    )
    await ctx.send(embed=embed, view=TicketView())
    await ctx.message.delete()

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

bot.run(token)
