import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
from datetime import datetime
from typing import Optional
import asyncio
import random
import re
import json
from datetime import timezone
import os

from dotenv import load_dotenv
from dotenv import load_dotenv

# โหลดค่าจากไฟล์ .env
load_dotenv()

try:
    with open("discord_users.json", "r") as f:
        users = json.load(f)
except:
    users = {"all": [], "banned": []}

def save_users():
    with open("discord_users.json", "w") as f:
        json.dump(users, f, indent=2)

def add_user(uid, name):
    if not any(u["id"] == uid for u in users["all"]):
        users["all"].append({"id": uid, "name": name})
        save_users()

def is_banned(uid):
    return any(b["id"] == uid for b in users["banned"])

def ban_user(uid):
    if not is_banned(uid):
        name = next((u["name"] for u in users["all"] if u["id"] == uid), str(uid))
        users["banned"].append({"id": uid, "name": name})
        save_users()
        return True
    return False

def unban_user(uid):
    users["banned"] = [b for b in users["banned"] if b["id"] != uid]
    save_users()

OWNER_ID = "890564632249516043"

# ---------------- ตัวแปรข้อความ ----------------

BOT_TOKEN = "MTU1MTQzMzkwODE0MTE2MjUzOA.GwqvXr.J6B42orXIhylcHUiQFu6HQmcOPCrz6zVKlLRfI"

FUNK_TEXT = """ # พ่อมึงตายแม่มึงตายไอ้สัสโง่เอ๋อขี้ยาติดม้าหลุดเม็ดหำเล็กไอ้เหี้ยอ้วนลูกทรพีแม่มึงเป็นกระหรี่เกิดมาทำเหี้ยไรไอ้ลูกกระหรี่ทำตัวไม่มีประโยชน์ดิสก็กระจอกหัวดิสไม่ทำไรเลยโดนยิงนี้โง่จัดควายก็ควายสมองหมาปัญญาควายสภาพดิสกระจอกดิสโง่ๆควายๆกลับเขมรไปไอ้ตัวลาบเดียวกูเอาข้าวเหนียวจิ้มแม่งสภาพพ่อแม่มึงเย็ดกันยังไงให้ได้ควายแถมลาบเขมรมาด้วยวะแม่มึงหีเท่าโอ่งมังกรหำพ่อมึงก็สั้นดำก็ดำ
"""

CHINESE_TEXT = """ # 你父母早就死了，你这个愚蠢、脑残、嗑冰毒成瘾、小鸡巴的肥猪。你个不孝的杂种——你妈就是个婊子；你他妈到底为什么要出生？你这没用的婊子养的；你在Discord上的表现简直可悲——你什么都不干，还老是被踢。你就是个彻头彻尾的蠢货，一头长着狗脑子和牛智商的蠢牛。你的设备烂透了——愚蠢、白痴，像头牛一样蠢。滚回柬埔寨去吧，你这坨“拉布”（larb）肉末——我真想拿糯米饭蘸着你吃。你父母到底是怎么交配的，才生出你这么个像牛一样的柬埔寨“拉布”肉末混种？你妈的逼大得像个装酒的大陶缸，而你爸的鸡巴又短又黑。你父母早就死了，你这个愚蠢、脑残、嗑冰毒成瘾、小鸡巴的肥猪。你个不孝的杂种——你妈就是个婊子；你他妈到底为什么要出生？你这没用的婊子养的；你在Discord上的表现简直可悲——你什么都不干，还老是被踢。你就是个彻头彻尾的蠢货，一头长着狗脑子和牛智商的蠢牛。你的设备烂透了——愚蠢、白痴，像头牛一样蠢。滚回柬埔寨去吧，你这坨“拉布”（larb）肉末——我真想拿糯米饭蘸着你吃。你父母到底是怎么交配的，才生出你这么个像牛一样的柬埔寨“拉布”肉末混种？你妈的逼大得像个装酒的大陶缸，而你爸的鸡巴又短又黑。
"""

KHMER_TEXT = """
# ឪពុកម្តាយឯងងាប់អស់ហើយ អាល្ងង់ អាខួរក្បាលខូច អាជាប់ញៀនថ្នាំមេត (meth) អាអាអូនតូចកំប៉ិកកំប៉ុក អាធាត់ស្អុយ។ អាអត់កតញ្ញូ—ម្តាយឯងជាស្រីពេស្យា; ឯងកើតមកធ្វើស្អី? អាឥតប្រយោជន៍ កូនស្រីពេស្យា; របៀបលេង Discord របស់ឯងគឺហួសចិត្តណាស់—ឯងមិនធ្វើស្អីសោះ ហើយតែងតែត្រូវគេទាត់ចេញ។ ឯងជាអាល្ងង់ពេញទំហឹង ជាអាគោល្ងង់ដែលមានខួរក្បាលឆ្កែ និងបញ្ញាគោ។ ឧបករណ៍លេងហ្គេមរបស់ឯងគឺសំរាម—ល្ងង់ខ្លៅ ឆ្កួតៗ ដូចគោ។ ត្រឡប់ទៅស្រុកខ្មែរវិញទៅ អាដុំឡាប (larb)—គេយកបាយដំណើបមកជ្រលក់ស៊ីឯងហ្នឹង។ តើឪពុកម្តាយឯងរួមភេទរបៀបណាបានជាបង្កើតបានកូនកាត់ខ្មែរ-ឡាប (larb) ដែលមានរូបរាងដូចគោបែបនេះ? ប្រដាប់ភេទម្តាយឯងធំដូចពាងមង្គលការ ហើយលិង្គឪពុកឯងខ្លី ហើយខ្មៅងងឹត។ឪពុកម្តាយឯងងាប់អស់ហើយ អាល្ងង់ អាខួរក្បាលខូច អាជាប់ញៀនថ្នាំមេត (meth) អាអាអូនតូចកំប៉ិកកំប៉ុក អាធាត់ស្អុយ។ អាអត់កតញ្ញូ—ម្តាយឯងជាស្រីពេស្យា; ឯងកើតមកធ្វើស្អី? អាឥតប្រយោជន៍ កូនស្រីពេស្យា; របៀបលេង Discord របស់ឯងគឺហួសចិត្តណាស់—ឯងមិនធ្វើស្អីសោះ ហើយតែងតែត្រូវគេទាត់ចេញ។ ឯងជាអាល្ងង់ពេញទំហឹង ជាអាគោល្ងង់ដែលមានខួរក្បាលឆ្កែ និងបញ្ញាគោ។ ឧបករណ៍លេងហ្គេមរបស់ឯងគឺសំរាម—ល្ងង់ខ្លៅ ឆ្កួតៗ ដូចគោ។ ត្រឡប់ទៅស្រុកខ្មែរវិញទៅ អាដុំឡាប (larb)—គេយកបាយដំណើបមកជ្រលក់ស៊ីឯងហ្នឹង។ តើឪពុកម្តាយឯងរួមភេទរបៀបណាបានជាបង្កើតបានកូនកាត់ខ្មែរ-ឡាប (larb) ដែលមានរូបរាងដូចគោបែបនេះ? ប្រដាប់ភេទម្តាយឯងធំដូចពាងមង្គលការ ហើយលិង្គឪពុកឯងខ្លី ហើយខ្មៅងងឹត។ឪពុកម្តាយឯងងាប់អស់ហើយ អាល្ងង់ អាខួរក្បាលខូច អាជាប់ញៀនថ្នាំមេត (meth) អាអាអូនតូចកំប៉ិកកំប៉ុក អាធាត់ស្អុយ។ អាអត់កតញ្ញូ—ម្តាយឯងជាស្រីពេស្យា; ឯងកើតមកធ្វើស្អី? អាឥតប្រយោជន៍ កូនស្រីពេស្យា; របៀបលេង Discord របស់ឯងគឺហួសចិត្តណាស់—ឯងមិនធ្វើស្អីសោះ ហើយតែងតែត្រូវគេទាត់ចេញ។ ឯងជាអាល្ងង់ពេញទំហឹង ជាអាគោល្ងង់ដែលមានខួរក្បាលឆ្កែ និងបញ្ញាគោ។ ឧបករណ៍លេងហ្គេមរបស់ឯងគឺសំរាម—ល្ងង់ខ្លៅ ឆ្កួតៗ ដូចគោ។ ត្រឡប់ទៅស្រុកខ្មែរវិញទៅ អាដុំឡាប (larb)—គេយកបាយដំណើបមកជ្រលក់ស៊ីឯងហ្នឹង។ តើឪពុកម្តាយឯងរួមភេទរបៀបណាបានជាបង្កើតបានកូនកាត់ខ្មែរ-ឡាប (larb) ដែលមានរូបរាងដូចគោបែបនេះ? ប្រដាប់ភេទម្តាយឯងធំដូចពាងមង្គលការ ហើយលិង្គឪពុកឯងខ្លី ហើយខ្មៅងងឹត។ឪពុកម្តាយឯងងាប់អស់ហើយ អាល្ងង់ អាខួរក្បាលខូច អាជាប់ញៀនថ្នាំមេត (meth) អាអាអូនតូចកំប៉ិកកំប៉ុក អាធាត់ស្អុយ។ អាអត់កតញ្ញូ—ម្តាយឯងជាស្រីពេស្យា; ឯងកើតមកធ្វើស្អី? អាឥតប្រយោជន៍ កូនស្រីពេស្យា; របៀបលេង Discord របស់ឯងគឺហួសចិត្តណាស់—ឯងមិនធ្វើស្អីសោះ ហើយតែងតែត្រូវគេទាត់ចេញ។ ឯងជាអាល្ងង់ពេញទំហឹង ជាអាគោល្ងង់ដែលមានខួរក្បាលឆ្កែ និងបញ្ញាគោ។ ឧបករណ៍លេងហ្គេមរបស់ឯងគឺសំរាម—ល្ងង់ខ្លៅ ឆ្កួតៗ ដូចគោ។ ត្រឡប់ទៅស្រុកខ្មែរវិញទៅ អាដុំឡាប (larb)—គេយកបាយដំណើបមកជ្រលក់ស៊ីឯងហ្នឹង។ តើឪពុកម្តាយឯងរួមភេទរបៀបណាបានជាបង្កើតបានកូនកាត់ខ្មែរ-ឡាប (larb) ដែលមានរូបរាងដូចគោបែបនេះ? ប្រដាប់ភេទម្តាយឯងធំដូចពាងមង្គលការ ហើយលិង្គឪពុកឯងខ្លី ហើយខ្មៅងងឹត។
"""

GIFT_TEXT = """
# ผมมีของลับให้สำหรับตัวหน้าหีอย่างพวกมึงดู
https://media.discordapp.net/attachments/1104642491052994661/1112241841564295198/file.gif?ex=6781f8ef&is=6780a76f&hm=7a8f7faf9325d6b9e19d61c6c7ceadf841dfaf441e4bb9aa8ea3c230c2cea1a6&
"""

PROMOTE_TEXT = """
# ผู้พัน | บริการบอทดิสคอร์ดยศราคาถูกมียิงเบอร์ฟรีและยิงดิสฟรี
**- แอดมินบริการตลอด✅️
- บอทใช้งานง่าย รันตลอด48ชั่วโมงแต่หัวดิสขี้เกียจรัน
- หากใช้ไม่เป็น หรืออยากสอบถามไรไห้ติดต่อเรามาได้ไม่พร้อมตอบตลอดเวลา
- มีของฟรีและอย่างอื่นอีกไม่เยอะ**

https://discord.gg/dFyGh7bw8w

"""



WARNING_EPHEMERAL = "# กูไม่รับผิดชอบกับสิ่งที่มึงทำ ไอ้ควาย\n**อยากหาความรู้ฉลาดเข้าสมองไปดิสอื่นเพราดิสกูก็ไปเอาของร้านอื่นมาด้วย หากอยากเข้าคลิกที่ลิ้งเลยไอ้ควาย**\n\nhttps://discord.gg/dFyGh7bw8w"



LAG = """ 😀😃😄😁😆😅😂🤣😊😇🙂🙃😉😌😍🥰😘😗😙😚😋😛😝😜🤪🤨🧐🤓😎🥸🤩🥳😏😒😞😔😟😕🙁☹️😣😖😫😩🥺😢😭😤😠😡🤬🤯😳🥵🥶😱😨😰😥😓🤗🤔🤭🤫🤥😶😐😑😬🙄😯😦😧😮😲🥱😴🤤😪😵🤐🥴🤢🤮🤧😷🤒🤕🤠😈👿👹👺🤡💩👻💀☠️👽👾🤖🎃😺😸😹😻😼😽🙀😿😾👋🤚🖐️✋🖖👌🤏✌️🤞🤟🤘🤙👈👉👆👇☝️👍👎✊👊🤛🤜👏🙌👐🤲🤝🙏✍️💅🤳💪🦾🦿🦵🦶👂🦻👃🧠🫀🫁🦷🦴👀👁️👅👄🫦👶🧒👦👧🧑👱👨🧔👨‍🦰👨‍🦱👨‍🦳👨‍🦲👩👱‍♀️👩‍🦰👩‍🦱👩‍🦳👩‍🦲🧓👴👵🙍🙎🙅🙆💁🙋🧏🙇🤦🤷👮🕵️💂👷🤴👸👳👲🧕🤵👰🤰🤱👼🎅🤶🦸🦹🧙🧚🧛🧜🧝🧞🧟💆💇🚶🧍🧎🏃💃🕺🕴️👯🧖🧗🤺🏇⛷️🏂🏌️🏄🚣🏊⛹️🏋️🚴🚵🤸🤼🤽🤾🤹🧘🛀🛌👭👫👬💏💑👪🗣️👤👥🫂👣❤️🧡💛💚💙💜🖤🤍🤎💔❣️💕💞💓💗💖💘💝💟♥️💯💢💥💫💦💨🕳️💬💭💤👓🕶️🥼🦺👔👕👖🧣🧤🧥🧦👗👘🥻🩱🩲🩳👙👚👛👜👝🎒👞👟🥾🥿👠👡🩰👢👑👒🎩🎓🧢🪖⛑️📿💄💍💎🔇🔈🔉🔊📢📣📯🔔🔕🎼🎵🎶🎙️🎚️🎛️🎤🎧📻🎷🪗🎸🎹🎺🎻🪕🥁🪘📱📲☎️📞📟📠🔋🔌💻🖥️🖨️⌨️🖱️🖲️💽💾💿📀🧮🎥🎞️📽️🎬📺📷📸📹📼🔍🔎🕯️💡🔦🏮🪔📔📕📖📗📘📙📚📓📒📃📜📄📰🗞️📑🔖🏷️💰🪙💴💵💶💷💸💳🧾✉️📧📨📩📤📥📦📫📪📬📭📮🗳️✏️✒️🖋️🖊️🖌️🖍️📝💼📁📂🗂️📅📆🗒️🗓️📇📈📉📊📋📌📍📎🖇️📏📐✂️🗃️🗄️🗑️🔒🔓🔏🔐🔑🗝️🔨🪓⛏️⚒️🛠️🗡️⚔️🔫🪃🏹🛡️🪚🔧🪛🔩⚙️🗜️⚖️🦯🔗⛓️🪝🧰🧲🪜⚗️🧪🧫🧬🔬🔭📡💉🩸💊🩹🩺🚪🛗🪞🪟🛏️🛋️🪑🚽🪠🚿🛁🪤🪒🧴🧷🧹🧺🧻🪣🧼🫧🪥🧽🧯🛒🚮🚰♿🚹🚺🚻🚼🚾🛂🛃🛄🛅🚸⚠️🚫🚳🚭🚯🚱🚷📵🔞☢️☣️⬆️↗️➡️↘️⬇️↙️⬅️↖️↕️↔️↩️↪️⤴️⤵️🔃🔄🔙🔚🔛🔜🔝🛐⚛️🕉️✡️☸️☯️✝️☦️☪️☮️🕎🔯♈♉♊♋♌♍♎♏♐♑♒♓⛎🔀🔁🔂▶️⏩⏭️⏯️◀️⏪⏮️🔼⏫🔽⏬⏸️⏹️⏺️⏏️🎦🔅🔆📶📳📴♀️♂️⚧️✖️➕➖➗🟰♾️‼️⁉️❓❔❕❗〰️💱💲⚕️♻️⚜️🔱📛🔰⭕✅☑️✔️❌❎➰➿〽️✳️✴️❇️©️®️™️#️⃣*️⃣0️⃣1️⃣2️⃣3️⃣4️⃣5️⃣6️⃣7️⃣8️⃣9️⃣🔟🔠🔡🔢🔣🔤🅰️🆎🅱️🆑🆒🆓ℹ️🆔Ⓜ️🆕🆖🅾️🆗🅿️🆘🆙🆚🈁🈂️🈷️🈶🈯🉐🈹🈚🈲🉑🈸🈴🈳㊗️㊙️🈺🈵🔴🟠🟡🟢🔵🟣🟤⚫⚪🟥🟧🟨🟩🟦🟪🟫⬛⬜◼️◻️◾◽▪️▫️🔶🔷🔸🔹🔺🔻💠🔘🔳🔲🏁🚩🎌🏴🏳️🏳️‍🌈🏳️‍⚧️🏴‍☠️🐶🐱🐭🐹🐰🦊🐻🐼🐨🐯🦁🐮🐷🐸🐵🙈🙉🙊🐒🐔🐧🐦🐤🐣🐥🦆🦅🦉🦇🐺🐗🐴🦄🐝🪱🐛🦋🐌🐞🐜🪰🪲🪳🦟🦗🕷️🕸️🦂🐢🐍🦎🦖🦕🐙🦑🦐🦞🦀🐡🐠🐟🐬🐳🐋🦈🐊🐅🐆🦓🦍🦧🦣🐘🦛🦏🐪🐫🦒🦘🦬🐃🐂🐄🐎🐖🐏🐑🦙🐐🦌🐕🐩🦮🐕‍🦺🐈🐈‍⬛🪶🐓🦃🦤🦚🦜🦢🦩🕊️🐇🦝🦨🦡🦫🦦🦥🐁🐀🐿️🦔🐾🐉🐲🌵🎄🌲🌳🌴🪵🌱🌿☘️🍀🎍🪴🎋🍃🍂🍁🍄🐚🪨🌾💐🌷🌹🥀🌺🌸🌼🌻🌞🌝🌛🌜🌚🌕🌖🌗🌘🌑🌒🌓🌔🌙🌎🌍🌏🪐💫⭐🌟✨⚡☄️💥🔥🌪️🌈☀️🌤️⛅🌥️☁️🌦️🌧️⛈️🌩️🌨️❄️☃️⛄🌬️💨💧💦☔☂️🌊🌫️🍏🍎🍐🍊🍋🍌🍉🍇🍓🫐🍈🍒🍑🥭🍍🥥🥝🍅🍆🥑🥦🥬🥒🌶️🫑🌽🥕🫒🧄🧅🥔🍠🥐🥯🍞🥖🥨🧀🥚🍳🧈🥞🧇🥓🥩🍗🍖🌭🍔🍟🍕🥪🥙🧆🌮🌯🫔🥗🥘🫕🥫🍝🍜🍲🍛🍣🍱🥟🦪🍤🍙🍚🍘🍥🥠🥮🍢🍡🍧🍨🍦🥧🧁🍰🎂🍮🍭🍬🍫🍿🍩🍪🌰🥜🍯🥛🍼🫖☕🍵🧃🥤🧋🍶🍺🍻🥂🍷🥃🍸🍹🧉🍾🧊🥄🍴🍽️🥣🥡🥢🧂⚽🏀🏈⚾🥎🎾🏐🏉🥏🎱🪀🏓🏸🏒🏑🥍🏏🪃🥅⛳🪁🏹🎣🤿🥊🥋🎽🛹🛼🛷⛸️🥌🎿⛷️🏂🪂🏋️🤼🤸⛹️🤺🤾🏌️🏇🧘🏄🏊🤽🚣🧗🚵🚴🏆🥇🥈🥉🏅🎖️🏵️🎗️🎫🎟️🎪🤹🎭🩰🎨🎬🎤🎧🎼🎹🥁🎷🎺🎸🪕🎻🎲♟️🎯🎳🎮🎰🧩🚗🚕🚙🚌🚎🏎️🚓🚑🚒🚐🛻🚚🚛🚜🦯🦽🦼🛴🚲🛵🏍️🛺🚨🚔🚍🚘🚖🚡🚠🚟🚃🚋🚞🚝🚄🚅🚈🚂🚆🚇🚊🚉✈️🛫🛬🛩️💺🛰️🚀🛸🚁🛶⛵🚤🛥️🛳️⛴️🚢⚓⛽🚧🚦🚥🗺️🗿🗽🗼🏰🏯🏟️🎡🎢🎠⛲⛱️🏖️🏝️🏜️🌋⛰️🏔️🗻🏕️⛺🏠🏡🏘️🏚️🏗️🏭🏢🏬🏣🏤🏥🏦🏨🏪🏫🏩💒🏛️⛪🕌🕍🛕🕋⛩️🛤️🛣️🗾🎑🏞️🌅🌄🌠🎇🎆🌇🌆🏙️🌃🌌🌉🌁⌚📱📲💻⌨️🖥️🖨️🖱️🖲️🕹️🗜️💽💾💿📀📼📷📸📹🎥📽️🎞️📞☎️📟📠📺📻🎙️🎚️🎛️🧭⏱️⏲️⏰🕰️⌛⏳📡🔋🔌💡🔦🕯️🪔🧯🛢️💸💵💴💶💷🪙💰💳💎⚖️🪜🧰🪛🔧🔨⚒️🛠️⛏️🪚🔩⚙️🪤🧱⛓️🧲🔫💣🧨🪓🔪🗡️⚔️🛡️🚬⚰️🪦⚱️🏺🔮📿🧿🪬💈⚗️??🔬🕳️🩹🩺💊💉🩸🧬🦠🧫🧪🌡️🧹🪠🧺🧻🚽🚰🚿🛁🛀🧼🪥🪒🧽🪣🧴🛎️🔑🗝️🚪🪑🛋️🛏️🛌🧸🪆🖼️🪞🪟🛍️🛒🎁🎈🎏🎀🪄🪅🎊🎉🎎🏮🎐🧧✉️
📩📨📧📪📫📬📭📮📯📜📃📄📑🧾📊📈📉🗒️🗓️📆📅🗑️📇🗃️🗄️📋📁📂🗂️🗞️📰📓📔📒📕📗📘📙📚📖🔖🧷🔗📎🖇️📐📏🧮📌📍✂️🖊️🖋️✒️🖌️🖍️📝✏️🔍🔎🔏🔐🔒🔓"""



K_J = """ควายไอ้สัสจังไรอิขนหมอยดกกุจะไม่หยุดกุจะสร้างความรำคาญแปสมแท็กพวกมึงควายควยสัสจังไรขนหมอยดกแม่มึงตายพ่อมึงตายไอ้ชิงหมาเกิดมึงเกิดมาทำไมวะควายชิบหายสัสไอ้เหี้ยโง่ไอ้ชาติหมามาเกิดไอ้เหี้ย2ขาไอ้ควายไอ้หำไซส์34หี34@everyone@everyone@everyone@everyone@everyone@everyone@everyone@everyone@everyone@everyone@everyone@everyone@everyone@everyone@everyone@everyone@everyone@everyone@everyone@everyone@everyone@everyone@everyone@everyone@everyone@everyone@everyone@everyone@everyone@everyone@everyone@everyone@everyone@everyone@everyone@everyone@everyone@everyone@everyone@everyone@everyone@everyone@everyone@everyone@everyone@everyone@everyone@everyone@everyone@everyone@everyone@everyone@everyone@everyone@everyone@everyone@everyone@everyone@everyone@everyone@everyone@everyone@everyone@everyone@everyone@everyone@everyone@everyone@everyone@everyone@everyone@everyone@everyone@everyone@everyone@everyone@everyone@everyone@everyone@everyone@everyone@everyone
"""



NSFW_IMAGES = [
    "https://api-cdn.rule34.xxx/images/2090/faca750621a0fa383d85dcf9a24b8b214209c302.gif",
    "https://api-cdn.rule34.xxx/images/1673/00758e80ccd868c658e41b03b94c29d0.jpeg",
    "https://api-cdn.rule34.xxx/images/2602/d535d9da2b0b23fce2429d17f7b6337d.png",
    "https://api-cdn.rule34.xxx/images/4611/07a18dffc3d59537e86ab55b214a54d7.jpeg",
    "https://api-cdn.rule34.xxx/images/1403/0551eec4b0a42e240fe7896728bb9807.jpeg",
    "https://api-cdn.rule34.xxx/images/1175/d7c5cccaca0b139875f9d9dd7da63f78.png",
    "https://api-cdn.rule34.xxx/images/2369/b580c0100ad26817e3f17472a81764a5.jpeg",
    "https://api-cdn.rule34.xxx/images/1974/531348a6d9d88a96ed8564cd1647d8bf.jpeg",
    "https://api-cdn.rule34.xxx/images/2038/8730aa96f0e3820a902206d41e488249.png",
    "https://api-cdn.rule34.xxx/images/1747/efe0ae93d490ccb373d2d77e6a18c7b6.png",
    "https://api-cdn.rule34.xxx/images/1350/8efd1a280d5dc98b5591de852cae9879.png",
    "https://api-cdn.rule34.xxx/images/7244/3c80f6afb64e72ea1b2092765495da48.png",
    "https://api-cdn.rule34.xxx/images/1735/5a63309f4d3ce95862e7cf159f160e7c.jpeg",
    "https://api-cdn.rule34.xxx/images/2861/617d8e5508fd033484e3d0514d9192c8.png",
    "https://api-cdn.rule34.xxx/images/4097/d365ad60eebfb031b02ec4d02f1901e999d08cab.png",
    "https://api-cdn.rule34.xxx/images/3968/304bdfceb5483fafedd0938b1d37451e.jpeg",
    "https://api-cdn.rule34.xxx/images/1835/7c6d2661d7d71ece31af506efc69ae18.png",
    "https://api-cdn.rule34.xxx/images/4118/99941186e137f7b375d9c3562f0fd4be.jpeg",
    "https://api-cdn.rule34.xxx/images/1375/ae31780729432267b778ed1fbc29badc.png",
    "https://api-cdn.rule34.xxx/images/5181/09c454e6985e85d21195bbb43d41ae8e.jpeg",
    "https://api-cdn.rule34.xxx/images/2104/42681bf7fbf3f1e4f0e68b18a100925e.png",
    "https://api-cdn.rule34.xxx/images/2484/908dd4cb318fc3b2eced8b3d9e12b24e.jpeg",
    "https://api-cdn.rule34.xxx/images/1657/d6babedf13803477afd6408e45f98f48.jpeg",
    "https://api-cdn.rule34.xxx/images/617/5d77b717109645a987dc9d4ad2181885.gif",
    "https://api-cdn.rule34.xxx/images/2538/22ac05e168f7c72df4e4c035719a9d51.png",
    "https://api-cdn.rule34.xxx/images/1680/a2711caeccf4bb55a50771732f28385b.png",
    "https://api-cdn.rule34.xxx/images/1441/551275328f598eabc89e5d90f3f0105d.jpeg",
    "https://api-cdn.rule34.xxx/images/559/da3eda46d5f8f744918b7e3d18227488.png",
    "https://api-cdn.rule34.xxx/images/2319/2d90d4722beea42832a2eeac61567a4d.jpeg",
    "https://api-cdn.rule34.xxx/images/3188/08dad60f315d4d67ccf4693e20498f23.jpeg",
    "https://api-cdn.rule34.xxx/images/2727/4e444c16bc89afd389988230b09fe0b8.jpeg",
    "https://api-cdn.rule34.xxx/images/4693/1d1c27261b09f406f6f088e019941fdf.jpeg",
    "https://api-cdn.rule34.xxx/images/603/98dc8499f1f50a0b58709721c8c66825.jpeg",
    "https://api-cdn.rule34.xxx/images/5548/e128ed8c7c7c9469e92ced35655db03d.jpeg",
]



THAI_MONTHS = [
    "มกราคม","กุมภาพันธ์","มีนาคม","เมษายน","พฤษภาคม","มิถุนายน",
    "กรกฎาคม","สิงหาคม","กันยายน","ตุลาคม","พฤศจิกายน","ธันวาคม"
]



MAX_SPAM_PER_COMMAND = 30
DEFAULT_SPAM_COUNT = 10


class DiscordApiManager:
    def __init__(self, session: aiohttp.ClientSession):
        self.session = session

    async def fetch_nsfw_image(self) -> str:
        url = "https://api.waifu.pics/nsfw/waifu"
        try:
            async with self.session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("url", "❌ ไม่สามารถดึงรูปภาพได้")
                return f"❌ API ตอบสถานะ {resp.status}"
        except Exception as e:
            return f"❌ เกิดข้อผิดพลาด: {str(e)}"


class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(command_prefix="!", intents=intents)
        self.session: aiohttp.ClientSession | None = None
        self.api_manager: DiscordApiManager | None = None

    async def setup_hook(self):
        self.session = aiohttp.ClientSession()
        self.api_manager = DiscordApiManager(self.session)

        try:
            synced = await self.tree.sync()
            print(f"Synced {len(synced)} slash command(s).")
        except Exception as e:
            print(f"Failed to sync slash commands: {e}")

    async def on_ready(self):
        print(f"Logged in as {self.user} ({self.user.id})")
        print("Bot is ready and listening for commands.")
        print("==============================")

    async def close(self):
        await super().close()
        if self.session:
            await self.session.close()

    async def send_warning(self, interaction: discord.Interaction):
        await interaction.response.send_message(WARNING_EPHEMERAL, ephemeral=True)

    async def fast_spam(self, interaction: discord.Interaction, message_func, count: int):
        for i in range(count):
            try:
                await message_func()
                await asyncio.sleep(0)
            except Exception as e:
                print(f"Error during spam (#{i+1}): {e}")

bot = MyBot()

async def check_user(interaction: discord.Interaction):
    uid = str(interaction.user.id)
    name = str(interaction.user)
    add_user(uid, name)
    if is_banned(uid):
        await interaction.response.send_message("❌ คุณถูกแบน ใช้คำสั่งไม่ได้ไอ่ควาย", ephemeral=True)
        return False
    return True

# ---------------- คำสั่งแบน/ปลดแบน ----------------
@bot.tree.command(name="userban", description="แบนและปลดแบนพวกมึงอย่าหาไช้")
@app_commands.describe(action="ban หรือ unban", user_id="ไอดีผู้ใช้")
async def userban(interaction: discord.Interaction, action: str, user_id: str):

    if str(interaction.user.id) != OWNER_ID:
        await interaction.response.send_message("สันหาไช้ระมึงก็บอกอยู่ไอ้ควาย", ephemeral=True)
        return

    if action.lower() == "ban":
        ban_user(user_id)
        await interaction.response.send_message(f"✅ แบนแล้ว {user_id}", ephemeral=True)

    elif action.lower() == "unban":
        unban_user(user_id)
        await interaction.response.send_message(f"✅ ปลดแบนแล้ว {user_id}", ephemeral=True)

    else:
        await interaction.response.send_message("❌ ใช้ ban หรือ unban เท่านั้น", ephemeral=True)



@bot.tree.command(name="พิมพ์", description="พิมพ์ข้อความส่งเองmessage")
@app_commands.describe(message="ข้อความ", count="จำนวนครั้ง (1-30, default 10)")
async def custom(interaction: discord.Interaction, message: str, count: Optional[int] = None):

    if not await check_user(interaction):
        return

    await bot.send_warning(interaction)
    spam_count = 10 if count is None else count

    if spam_count > MAX_SPAM_PER_COMMAND:
        await interaction.followup.send(f"# มันจำกัดเเค่{MAX_SPAM_PER_COMMAND}ข้อความต่อการเเสปมในเเต่ละครั้งไอ่ควาย ไอ่โง่ หัดดูบ้างดิ อ่านไอ่สัส ตามึงมีไว้ทำไมวะ ไว้ดูเเต่หีหรอมึง", ephemeral=True)
        return

    async def spam_content():
        await interaction.followup.send(message)

    await bot.fast_spam(interaction, spam_content, spam_count)



@bot.tree.command(name="ด่าดิสกระจอก", description="ด่ายาวๆ แบบควยๆ")
@app_commands.describe(count="จำนวนครั้งที่สแปม (1-30, ค่าเริ่มต้น 10)")
async def funk(interaction: discord.Interaction, count: Optional[int] = None):

    if not await check_user(interaction):
        return

    await bot.send_warning(interaction)
    spam_count = 10 if count is None else count

    if spam_count > MAX_SPAM_PER_COMMAND:
        await interaction.followup.send(f"# มันจำกัดเเค่{MAX_SPAM_PER_COMMAND}ข้อความต่อการเเสปมในเเต่ละครั้งไอ่ควาย ไอ่โง่ หัดดูบ้างดิ อ่านไอ่สัส ตามึงมีไว้ทำไมวะ ไว้ดูเเต่หีหรอมึง", ephemeral=True)
        return

    async def spam_content():
        await interaction.followup.send(FUNK_TEXT)

    await bot.fast_spam(interaction, spam_content, spam_count)



@bot.tree.command(name="แสปมบรรทัด", description="กูไม่รู้ว่าจะบอกไง")
@app_commands.describe(message="ข้อความ", repeat="จำนวนครั้งที่ขึ้นบรรทัดใหม่ (1-20)", count="จำนวนครั้งที่สแปม (1-30, default 10)")
async def fast_cmd(interaction: discord.Interaction, message: str, repeat: int, count: Optional[int] =  None):

    if not await check_user(interaction):
        return

    await bot.send_warning(interaction)

    repeat_count = max(1, min(repeat, 20))
    spam_count = 10 if count is None else count

    if spam_count > MAX_SPAM_PER_COMMAND:
        await interaction.followup.send(f"# มันจำกัดเเค่{MAX_SPAM_PER_COMMAND}ข้อความต่อการเเสปมในเเต่ละครั้งไอ่ควาย ไอ่โง่ หัดดูบ้างดิ อ่านไอ่สัส ตามึงมีไว้ทำไมวะ ไว้ดูเเต่หีหรอมึง", ephemeral=True)
        return

    full_message = "\n".join([message for _ in range(repeat_count)])

    async def spam_content():
        await interaction.followup.send(full_message)

    await bot.fast_spam(interaction, spam_content, spam_count)



@bot.tree.command(name="ภาษาอาหวัง", description="เเสปมจีน")
@app_commands.describe(count="จำนวนครั้งที่สแปม (1-30, ค่าเริ่มต้น 10)")
async def chinese_cmd(interaction: discord.Interaction, count: Optional[int] = None):

    if not await check_user(interaction):
        return

    await bot.send_warning(interaction)
    spam_count = 10 if count is None else count

    if spam_count > MAX_SPAM_PER_COMMAND:
        await interaction.followup.send(f"# มันจำกัดเเค่{MAX_SPAM_PER_COMMAND}ข้อความต่อการเเสปมในเเต่ละครั้งไอ่ควาย ไอ่โง่ หัดดูบ้างดิ อ่านไอ่สัส ตามึงมีไว้ทำไมวะ ไว้ดูเเต่หีหรอมึง", ephemeral=True)
        return

    async def spam_content():
        await interaction.followup.send(CHINESE_TEXT)

    await bot.fast_spam(interaction, spam_content, spam_count)



@bot.tree.command(name="เขมร", description="เเสปมด่าแบบพวกลาบภาษาเส้นหมอย")
@app_commands.describe(count="จำนวนครั้งที่สแปม (1-30, ค่าเริ่มต้น 10)")
async def khmer_cmd(interaction: discord.Interaction, count: Optional[int] = None):

    if not await check_user(interaction):
        return

    await bot.send_warning(interaction)

    spam_count_total = 6
    user_count = count if count is not None else 10

    if user_count > MAX_SPAM_PER_COMMAND:
        await interaction.followup.send(f"# มันจำกัดเเค่{MAX_SPAM_PER_COMMAND}ข้อความต่อการเเสปมในเเต่ละครั้งไอ่ควาย ไอ่โง่ หัดดูบ้างดิ อ่านไอ่สัส ตามึงมีไว้ทำไมวะ ไว้ดูเเต่หีหรอมึง", ephemeral=True)
        return

    spam_times = user_count if user_count is not None else 10

    async def spam_content():
        await interaction.followup.send(KHMER_TEXT)

    await bot.fast_spam(interaction, spam_content, spam_times)


def format_thai_date(dt):
    dt = dt.astimezone(timezone.utc)
    day = dt.day
    month = THAI_MONTHS[dt.month - 1]
    year = dt.year + 543
    hour = dt.hour
    minute = dt.minute
    return f"{day} {month} {year} {hour:02d}:{minute:02d}"

@bot.tree.command(name="หาข้อมูลด้วยไอดีมั้ง", description="ดูเวลาสร้างรูปและอีกนิดนึง")
@app_commands.describe(user_id="ไอดีผู้ใช้ Discord")
async def userinfo(interaction: discord.Interaction, user_id: str):

    if not await check_user(interaction):
        return

    await interaction.response.defer(ephemeral=True)

    try:
        user = await bot.fetch_user(int(user_id))
    except:
        await interaction.followup.send("❌ หาไอดีนี้ไม่เจอไอ้ควาย", ephemeral=True)
        return

    is_bot = "🤖 บอท" if user.bot else "👤 คน"
    created_en = user.created_at.strftime("%d %B %Y • %H:%M UTC")
    created_th = format_thai_date(user.created_at)
    avatar_url = user.display_avatar.url

    embed = discord.Embed(
        title="📌 ข้อมูลผู้ใช้ Discord นี้",
        color=0xff0055
    )
    embed.add_field(name="ชื่อผู้ใช้", value=f"`{user}`", inline=False)
    embed.add_field(name="ชื่อที่แสดง", value=f"`{user.display_name}`", inline=False)
    embed.add_field(name="ไอดี", value=f"`{user.id}`", inline=False)
    embed.add_field(name="เป็นคนหรือบอท", value=is_bot, inline=False)
    embed.add_field(
        name="สร้างบัญชี",
        value=f"🇬🇧 {created_en}\n🇹🇭 {created_th}",
        inline=False
    )

    embed.set_thumbnail(url=avatar_url)
    embed.set_image(url=avatar_url)
    embed.set_footer(text="กดที่รูปเพื่อดูเต็มหากอยากได้รูปไห้กดรูปแล้วกดสามจุดกดบันทึกไม่ก็ดาวโหลด")

    await interaction.followup.send(embed=embed, ephemeral=True)



@bot.tree.command(name="gift", description="มีของขวัญมาเเจกไอ้หน้าหี")
@app_commands.describe(count="จำนวนครั้งที่สแปม (1-30, ค่าเริ่มต้น 10)")
async def gift_cmd(interaction: discord.Interaction, count: Optional[int] = None):

    if not await check_user(interaction):
        return

    await bot.send_warning(interaction)

    spam_times = count if count is not None else 10

    if spam_times > MAX_SPAM_PER_COMMAND:
        await interaction.followup.send(f"# มันจำกัดเเค่{MAX_SPAM_PER_COMMAND}ข้อความต่อการเเสปมในแต่ละครั้งไอ่ควาย ไอ่โง่ หัดดูบ้างดิ อ่านไอ่สัส ตามึงมีไว้ทำไมวะ ไว้ดูเเต่หีหรอมึง", ephemeral=True)
        return

    async def send_gift_msg():
        await interaction.followup.send(GIFT_TEXT)

    await bot.fast_spam(interaction, send_gift_msg, spam_times)



@bot.tree.command(name="spam18", description="สุ่มส่งภาพ18")
@app_commands.describe(count="จำนวนครั้งที่สแปม (1-30, ค่าเริ่มต้น 10)")
async def spam18(interaction: discord.Interaction, count: Optional[int] = None):

    if not await check_user(interaction):
        return

    await bot.send_warning(interaction)

    spam_count = 10 if count is None else count

    if spam_count < 1 or spam_count > MAX_SPAM_PER_COMMAND:
        await interaction.followup.send(f"มันจำกัดเเค่{MAX_SPAM_PER_COMMAND}ข้อความต่อการเเสปมในเเต่ละครั้งไอ่ควาย ไอ่โง่ หัดดูบ้างดิ อ่านไอ่สัส ตามึงมีไว้ทำไมวะ ไว้ดูเเต่หีหรอมึง", ephemeral=True)
        return

    async def send_random_image():
        img_url = random.choice(NSFW_IMAGES)
        await interaction.followup.send(img_url)

    await bot.fast_spam(interaction, send_random_image, spam_count)



@bot.tree.command(name="promote-ดิสกุ", description="โปรโมทดิสกุและสิ่งที่กุทำ")
@app_commands.describe(count="จำนวนครั้งที่สแปม (1-30, ค่าเริ่มต้น 10)")
async def promote(interaction: discord.Interaction, count: Optional[int] = None):

    if not await check_user(interaction):
        return

    await bot.send_warning(interaction)
    spam_count = 10 if count is None else count

    if spam_count > MAX_SPAM_PER_COMMAND:
        await interaction.followup.send(f"# มันจำกัดเเค่{MAX_SPAM_PER_COMMAND}ข้อความต่อการเเสปมในเเต่ละครั้งไอ่ควาย ไอ่โง่ หัดดูบ้างดิ่ อ่านไอ่สัส ตามึงมีไว้ทำไมวะ ไว้ดูเเต่หีหรอมึง", ephemeral=True)
        return

    async def send_promote():
        await interaction.followup.send(PROMOTE_TEXT)

    await bot.fast_spam(interaction, send_promote, spam_count)



@bot.tree.command(name="lag", description="สแปมอิโมจิยาวๆ เพื่อเหี้ยอะไรก็ไม่รู้")
@app_commands.describe(count="จำนวนครั้งที่สแปม (1-30, ค่าเริ่มต้น 10)")
async def lag_cmd(interaction: discord.Interaction, count: Optional[int] = None):

    if not await check_user(interaction):
        return

    await bot.send_warning(interaction)

    spam_count = 10 if count is None else count

    if spam_count > MAX_SPAM_PER_COMMAND:
        await interaction.followup.send(f"# มันจำกัดเเค่{MAX_SPAM_PER_COMMAND}ข้อความต่อการเเสปมในเเต่ละครั้งไอ่ควาย ไอ่โง่ หัดดูบ้างดิ่ อ่านไอ่สัส ตามึงมีไว้ทำไมวะ ไว้ดูเเต่หีหรอมึง", ephemeral=True)
        return

    async def send_lag():
        await interaction.followup.send(LAG)

    await bot.fast_spam(interaction, send_lag, spam_count)



@bot.tree.command(name="แสปมแท็ก", description="สแปมแท็กรัวๆไห้ดิสนั้นแม่งรำคาญจนออก")
@app_commands.describe(count="จำนวนครั้งที่สแปม (1-30, ค่าเริ่มต้น 10)")
async def lag_cmd(interaction: discord.Interaction, count: Optional[int] = None):

    if not await check_user(interaction):
        return

    await bot.send_warning(interaction)

    spam_count = 10 if count is None else count

    if spam_count > MAX_SPAM_PER_COMMAND:
        await interaction.followup.send(f"# มันจำกัดเเค่{MAX_SPAM_PER_COMMAND}ข้อความต่อการเเสปมในเเต่ละครั้งไอ่ควาย ไอ่โง่ หัดดูบ้างดิ อ่านไอ่สัส ตามึงมีไว้ทำไมวะ ไว้ดูเเต่หีหรอมึง", ephemeral=True)
        return

    async def send_lag():
        await interaction.followup.send(K_J)

    await bot.fast_spam(interaction, send_lag, spam_count)



@bot.tree.command(name="spam-webhook", description="Spam Webhook กากๆ")
@app_commands.describe(
    webhook_url="ลิงก์ Webhook ที่ต้องการสแปม",
    message="ข้อความที่ต้องการสแปม",
    count="จำนวนครั้งที่สแปม (1-25, ค่าเริ่มต้น 5)",
    name="เปลี่ยนชื่อ Webhook (ไม่บังคับ)",
    avatar_url="เปลี่ยนรูปโปรไฟล์ Webhook (ไม่บังคับ)",
    delete_webhook="ลบ Webhook หลังสแปมเสร็จ (ไม่บังคับ)"
)
async def spam_webhook(
    interaction: discord.Interaction,
    webhook_url: str,
    message: str,
    count: Optional[int] = None,
    name: Optional[str] = None,
    avatar_url: Optional[str] = None,
    delete_webhook: Optional[bool] = False
):
    await bot.send_warning(interaction)

    spam_count = 5 if count is None else count

    if spam_count > MAX_SPAM_PER_COMMAND:
        await interaction.followup.send(f"# มันจำกัดเเค่{MAX_SPAM_PER_COMMAND}ข้อความต่อการเเสปมในเเต่ละครั้งไอ่ควาย ไอ่โง่ หัดดูบ้างดิ อ่านไอ่สัส ตามึงมีไว้ทำไมวะ ไว้ดูเเต่หีหรอมึง", ephemeral=True)
        return

    if not webhook_url.startswith("https://discord.com/api/webhooks/"):
        await interaction.followup.send("❌ ลิงก์ Webhook ไม่ถูกต้อง", ephemeral=True)
        return

    try:
        parts = webhook_url.split("/")
        webhook_id = parts[-2]
        webhook_token = parts[-1]
    except IndexError:
        await interaction.followup.send("❌ รูปแบบ Webhook URL ผิดพลาด", ephemeral=True)
        return

    async def send_to_webhook():
        payload = {
            "content": message,
            "username": name,
            "avatar_url": avatar_url
        }
        payload = {k: v for k, v in payload.items() if v is not None}

        url = f"https://discord.com/api/webhooks/{webhook_id}/{webhook_token}"
        headers = {"Content-Type": "application/json"}

        try:
            async with bot.session.post(url, json=payload, headers=headers) as resp:
                if resp.status == 204:
                    pass
                else:
                    print(f"⚠️ Webhook ส่งไม่สำเร็จ: {resp.status}")
        except Exception as e:
            print(f"❌ เกิดข้อผิดพลาดในการส่ง Webhook: {e}")

    await bot.fast_spam(interaction, send_to_webhook, spam_count)

    if delete_webhook:
        try:
            delete_url = f"https://discord.com/api/webhooks/{webhook_id}/{webhook_token}"
            async with bot.session.delete(delete_url) as resp:
                if resp.status == 204:
                    await interaction.followup.send("✅ Webhook ถูกลบเรียบร้อยแล้ว", ephemeral=True)
                else:
                    await interaction.followup.send(f"❌ ไม่สามารถลบ Webhook ได้ (สถานะ: {resp.status})", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ เกิดข้อผิดพลาดในการลบ Webhook: {e}", ephemeral=True)

if __name__ == "__main__":
    if TOKEN = os.getenv("bomdis1_token"):
        print("❌ กรุณาใส่ Token บอทของคุณในตัวแปร BOT_TOKEN!")
    else:
        try:
            bot.run(TOKEN)
        except discord.LoginFailure:
            print("❌ Token บอทไม่ถูกต้อง!")
        except Exception as e:
            print(f"❌ เกิดข้อผิดพลาดในการรันบอท: {e}")
