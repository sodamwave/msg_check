import discord
import os
import re
import threading
# Flask에서 render_template 함수를 추가로 가져옵니다.
from flask import Flask, jsonify, render_template
from datetime import datetime, timezone, timedelta


# -------------------------------------
# 설정 (이 부분은 그대로 둡니다)
# -------------------------------------
DISCORD_TOKEN = os.environ.get('DISCORD_TOKEN')
TARGET_CHANNEL_ID = int(os.environ.get('TARGET_CHANNEL_ID'))

# -------------------------------------
# 데이터 저장소 및 웹 서버 초기화 (이 부분은 그대로 둡니다)
# -------------------------------------
computer_statuses = {}
status_lock = threading.Lock()
app = Flask(__name__)

# -------------------------------------
# 디스코드 봇 로직 (이 부분은 그대로 둡니다)
# -------------------------------------
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
UUID_PATTERN = re.compile(r'([0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{12})', re.IGNORECASE)

def parse_and_update_status(message_content):
    uuid_match = UUID_PATTERN.search(message_content)
    if not uuid_match:
        return
    uuid = uuid_match.group(1).upper()
    status = None
    if "__시작" in message_content:
        status = "시작"
    elif "__종료" in message_content:
        status = "종료"
    if status:
        kst = timezone(timedelta(hours=9))
        timestamp = datetime.now(kst).isoformat()
        with status_lock:
            computer_statuses[uuid] = {
                'status': status,
                'last_update': timestamp
            }
        print(f"[상태 업데이트] UUID: {uuid}, 상태: {status}, 시간: {timestamp}")

@client.event
async def on_ready():
    print(f'{client.user} (으)로 로그인했습니다.')
    channel = client.get_channel(TARGET_CHANNEL_ID)
    if channel:
        print(f"'{channel.name}' 채널의 최근 1000개 메시지를 스캔하여 초기 상태를 설정합니다.")
        async for message in channel.history(limit=1000):
            parse_and_update_status(message.content)
        print("초기 상태 설정 완료.")

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.channel.id == TARGET_CHANNEL_ID:
        parse_and_update_status(message.content)

# -------------------------------------
# Flask 웹 API 로직 (★★★ 이 부분이 변경됩니다 ★★★)
# -------------------------------------
@app.route('/')
def home():
    """
    기존에는 단순 텍스트를 반환했지만, 이제는 templates 폴더의
    index.html 파일을 웹페이지로 만들어서 보여줍니다.
    """
    return render_template('index.html')

@app.route('/status')
def get_statuses():
    """모든 컴퓨터의 현재 상태를 JSON 형태로 반환합니다. (이 부분은 그대로)"""
    with status_lock:
        return jsonify(computer_statuses)

# -------------------------------------
# 프로그램 실행 (이 부분은 그대로 둡니다)
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

