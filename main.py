import discord
import os
import re
import threading
from flask import Flask, jsonify, render_template
from datetime import datetime, timezone, timedelta

# -------------------------------------
# 설정
# -------------------------------------
DISCORD_TOKEN = os.environ.get('DISCORD_TOKEN')
TARGET_CHANNEL_ID = int(os.environ.get('TARGET_CHANNEL_ID'))

# -------------------------------------
# 데이터 저장소 및 웹 서버 초기화
# -------------------------------------
# {'uuid': {'status': '...', 'event_time': 'HH:MM:SS', 'last_update': '...'}}
computer_statuses = {}
status_lock = threading.Lock()
app = Flask(__name__)

# -------------------------------------
# 디스코드 봇 로직
# -------------------------------------
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# 정규식 패턴 추가
UUID_PATTERN = re.compile(r'([0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{12})', re.IGNORECASE)
# ★★★ 시간(HH:MM:SS)을 추출하기 위한 정규식 추가 ★★★
TIME_PATTERN = re.compile(r'\[\d{4}-\d{2}-\d{2} (\d{2}:\d{2}:\d{2})\]')

def parse_and_update_status(message_content):
    """메시지 내용을 파싱하여 상태와 시간을 함께 업데이트합니다."""
    
    uuid_match = UUID_PATTERN.search(message_content)
    if not uuid_match:
        return

    uuid = uuid_match.group(1).upper()
    status = None
    
    # ★★★ 시간 정보 추출 ★★★
    time_match = TIME_PATTERN.search(message_content)
    event_time = time_match.group(1) if time_match else "N/A"

    if "__시작" in message_content:
        status = "시작"
    elif "__종료" in message_content:
        status = "종료"
    
    if status:
        kst = timezone(timedelta(hours=9))
        timestamp = datetime.now(kst).isoformat()

        with status_lock:
            # ★★★ event_time을 함께 저장 ★★★
            computer_statuses[uuid] = {
                'status': status,
                'event_time': event_time,
                'last_update': timestamp
            }
        print(f"[상태 업데이트] UUID: {uuid}, 상태: {status}, 시간: {event_time}")

@client.event
async def on_ready():
    """봇이 준비되었을 때 실행됩니다."""
    print(f'{client.user} (으)로 로그인했습니다.')
    channel = client.get_channel(TARGET_CHANNEL_ID)
    if channel:
        print(f"'{channel.name}' 채널의 최근 1000개 메시지를 스캔하여 초기 상태를 설정합니다.")
        
        # ★★★ 순서 문제를 해결하기 위해, 메시지를 리스트로 받은 뒤 역순으로 처리 ★★★
        # channel.history()는 최신 메시지부터 가져오므로, reversed()를 사용해 가장 오래된 메시지부터 처리합니다.
        messages = [message async for message in channel.history(limit=1000)]
        for message in reversed(messages):
            parse_and_update_status(message.content)
            
        print("초기 상태 설정 완료.")

@client.event
async def on_message(message):
    """메시지가 수신될 때마다 실행됩니다."""
    if message.author == client.user:
        return
    if message.channel.id == TARGET_CHANNEL_ID:
        parse_and_update_status(message.content)

# -------------------------------------
# Flask 웹 API 로직 (변경 없음)
# -------------------------------------
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/status')
def get_statuses():
    with status_lock:
        return jsonify(computer_statuses)

# -------------------------------------
# 프로그램 실행 (변경 없음)
# -------------------------------------
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
