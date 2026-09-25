# run_multiple_bots.py
import subprocess
import os

if __name__ == "__main__":
    # ค้นหาไฟล์ .py ทั้งหมดในโฟลเดอร์ปัจจุบัน ยกเว้นไฟล์สคริปต์ตัวนี้เอง
    current_script = os.path.basename(__file__)
    bot_files = [f for f in os.listdir('.') if f.endswith('.py') and f != current_script]

    print(f"พบไฟล์บอททั้งหมด {len(bot_files)} ไฟล์: {bot_files}")

    processes = []
    for bot_file in bot_files:
        print(f"กำลังเริ่มรัน: {bot_file}")
        process = subprocess.Popen(['python', bot_file])
        processes.append(process)

    for process in processes:
        process.wait()
