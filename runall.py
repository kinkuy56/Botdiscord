from flask import Flask
import subprocess
import os
import threading

app = Flask(__name__)

@app.route('/')
def home():
    return "All bots are running 24/7!"

def run_all_bots():
    # ค้นหาไฟล์ .py ทั้งหมดในโฟลเดอร์ ยกเว้นไฟล์ตัวมันเอง
    current_script = os.path.basename(__file__)
    bot_files = [f for f in os.listdir('.') if f.endswith('.py') and f != current_script]

    print(f"พบไฟล์บอททั้งหมด {len(bot_files)} ไฟล์: {bot_files}")

    processes = []
    for bot_file in bot_files:
        print(f"กำลังเริ่มรัน: {bot_file}")
        # ใช้ python3 เพื่อความชัวร์บน Linux server ของ Render
        process = subprocess.Popen(['python3', bot_file])
        processes.append(process)

    for process in processes:
        process.wait()

if __name__ == "__main__":
    # แยก Thread ไปรันบอททั้งหมด เพื่อไม่ให้ไปบล็อกเว็บเซิร์ฟเวอร์ของ Flask
    bot_thread = threading.Thread(target=run_all_bots)
    bot_thread.daemon = True
    bot_thread.start()

    # รันเว็บเซิร์ฟเวอร์ Flask (Render บังคับให้ต้องมีพอร์ตเปิดรับเว็บ)
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
