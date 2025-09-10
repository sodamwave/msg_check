import discord
import os
import re
import threading
from flask import Flask, jsonify, render_template
from datetime import datetime, timezone, timedelta

# -------------------------------------
# 설정 (UUID_MAP 등 이전 내용은 그대로 유지)
# -------------------------------------
DISCORD_TOKEN = os.environ.get('DISCORD_TOKEN')
TARGET_CHANNEL_ID = int(os.environ.get('TARGET_CHANNEL_ID'))

UUID_MAP = {
    "B6254D56-1931-8E9A-6F2C-C413BCA4F6CB": "1번 컴퓨터", "00F54D56-3471-F7DA-19A0-25962FD3EDD4": "2번 컴퓨터",
    "698A4D56-6628-2370-1786-F01F6FB8E011": "3번 컴퓨터", "758B4D56-184F-DCCE-BA13-5125C618E676": "4번 컴퓨터",
    "DF1F4D56-5DC5-8F54-464D-64A208A271FA": "5번 컴퓨터", "C6144D56-3194-835A-DBC7-220B047B5C38": "6번 컴퓨터",
    "AD164D56-9697-F145-06F9-234427A81542": "7번 컴퓨터", "D65F4D56-1EF8-F9E0-4D09-5EAB7DD1FF23": "8번 컴퓨터",
    "8F3D4D56-F7B9-2BF2-9759-BC51850C4FB5": "9번 컴퓨터", "38604D56-CA2C-9EAB-EE8C-A5027CA9DF1F": "10번 컴퓨터",
    # ... (나머지 UUID 목록은 생략) ...
    "6F544D56-2B92-1F01-86F4-AC02B3A075E5": "239번 컴퓨터",
    "": "UUID 없음"
}

computer_statuses = {}
status_lock = threading.Lock()
app = Flask(__name__)

def initialize_statuses():
    for name in UUID_MAP.values():
        if name not in computer_statuses:
            computer_statuses[name] = { 'status': '알 수 없음', 'log_timestamp': '-', 'last_update': datetime.now(timezone(timedelta(hours=9))).isoformat() }
    empty_uuid_numbers = [157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 235, 236, 237, 238, 240]
    for num in empty_uuid_numbers:
        name = f"{num}번 컴퓨터"
        computer_statuses[name] = { 'status': 'UUID 없음', 'log_timestamp': '-', 'last_update': datetime.now(timezone(timedelta(hours=9))).isoformat() }

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

UUID_PATTERN = re.compile(r'([0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{12})', re.IGNORECASE)
# ★★★ 정규식 변경: 날짜와 시간을 모두 포함하여 캡처 ★★★
LOG_TIMESTAMP_PATTERN = re.compile(r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\]')

def parse_and_update_status(message_content):
    uuid_match = UUID_PATTERN.search(message_content)
    uuid = uuid_match.group(1).upper() if uuid_match else ""
    display_name = UUID_MAP.get(uuid, uuid) if uuid else UUID_MAP.get("")

    status = None
    # ★★★ 전체 일시 추출 ★★★
    timestamp_match = LOG_TIMESTAMP_PATTERN.search(message_content)
    log_timestamp = timestamp_match.group(1) if timestamp_match else "N/A"

    if "__시작" in message_content: status = "시작"
    elif "__종료" in message_content: status = "종료"
    
    if status and display_name:
        kst = timezone(timedelta(hours=9))
        server_check_time = datetime.now(kst).isoformat()
        with status_lock:
            # ★★★ 'event_time' 대신 'log_timestamp'로 저장 ★★★
            computer_statuses[display_name] = {
                'status': status,
                'log_timestamp': log_timestamp,
                'last_update': server_check_time
            }
        print(f"[상태 업데이트] {display_name}, 상태: {status}, 로그일시: {log_timestamp}")

# on_ready, on_message 및 나머지 코드는 이전과 동일하므로 생략...
@client.event
async def on_ready():
    print(f'{client.user} (으)로 로그인했습니다.')
    initialize_statuses()
    channel = client.get_channel(TARGET_CHANNEL_ID)
    if channel:
        print(f"'{channel.name}' 채널의 최근 1000개 메시지를 스캔합니다.")
        messages = [message async for message in channel.history(limit=1000)]
        for message in reversed(messages):
            parse_and_update_status(message.content)
        print("초기 상태 설정 완료.")

@client.event
async def on_message(message):
    if message.author == client.user: return
    if message.channel.id == TARGET_CHANNEL_ID:
        parse_and_update_status(message.content)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/status')
def get_statuses():
    with status_lock:
        return jsonify(computer_statuses)

def run_flask():
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    if not DISCORD_TOKEN or not TARGET_CHANNEL_ID:
        print("오류: DISCORD_TOKEN 또는 TARGET_CHANNEL_ID 환경 변수가 설정되지 않았습니다.")
    else:
        flask_thread = threading.Thread(target=run_flask)
        flask_thread.daemon = True
        flask_thread.start()
        client.run(DISCORD_TOKEN)
