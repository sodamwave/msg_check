import discord
import os
import re
import threading
from flask import Flask, jsonify
from datetime import datetime, timezone, timedelta

# -------------------------------------
# 설정
# -------------------------------------
# Railway 같은 배포 환경에서는 환경 변수를 사용합니다.
# 로컬에서 테스트할 경우, 직접 값을 할당하거나 .env 파일을 사용할 수 있습니다.
DISCORD_TOKEN = os.environ.get('DISCORD_TOKEN')
TARGET_CHANNEL_ID = int(os.environ.get('TARGET_CHANNEL_ID'))

# -------------------------------------
# 데이터 저장소 및 웹 서버 초기화
# -------------------------------------
# 각 UUID별 최신 상태를 저장할 딕셔너리
# {'uuid': {'status': '시작' or '종료', 'timestamp': '... Z'}}
computer_statuses = {}
status_lock = threading.Lock()  # 동시 접근을 막기 위한 Lock

# Flask 웹 서버 애플리케이션 생성
app = Flask(__name__)

# -------------------------------------
# 디스코드 봇 로직
# -------------------------------------
intents = discord.Intents.default()
intents.message_content = True  # 메시지 내용을 읽기 위한 인텐트
client = discord.Client(intents=intents)

# UUID 패턴 (대소문자 구분 없음)
# 예: BF244D56-A402-58BB-F624-43B487FB9BE7
UUID_PATTERN = re.compile(r'([0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{12})', re.IGNORECASE)

def parse_and_update_status(message_content):
    """메시지 내용을 파싱하여 상태를 업데이트합니다."""
    
    # UUID 찾기
    uuid_match = UUID_PATTERN.search(message_content)
    if not uuid_match:
        return

    uuid = uuid_match.group(1).upper() # UUID를 대문자로 통일
    status = None

    if "__시작" in message_content:
        status = "시작"
    elif "__종료" in message_content:
        status = "종료"
    
    if status:
        # 한국 시간(KST, UTC+9)으로 현재 시간 기록
        kst = timezone(timedelta(hours=9))
        timestamp = datetime.now(kst).isoformat()

        # Lock을 사용하여 안전하게 데이터 업데이트
        with status_lock:
            computer_statuses[uuid] = {
                'status': status,
                'last_update': timestamp
            }
        print(f"[상태 업데이트] UUID: {uuid}, 상태: {status}, 시간: {timestamp}")


@client.event
async def on_ready():
    """봇이 준비되었을 때 실행됩니다."""
    print(f'{client.user} (으)로 로그인했습니다.')
    print('지정된 채널의 메시지를 감시합니다...')

    # 봇이 시작될 때 기존 채널 메시지를 읽어와서 초기 상태를 설정할 수 있습니다.
    channel = client.get_channel(TARGET_CHANNEL_ID)
    if channel:
        print(f"'{channel.name}' 채널의 최근 1000개 메시지를 스캔하여 초기 상태를 설정합니다.")
        async for message in channel.history(limit=1000):
            parse_and_update_status(message.content)
        print("초기 상태 설정 완료.")


@client.event
async def on_message(message):
    """메시지가 수신될 때마다 실행됩니다."""
    # 봇 자신의 메시지는 무시
    if message.author == client.user:
        return

    # 목표 채널의 메시지만 처리
    if message.channel.id == TARGET_CHANNEL_ID:
        parse_and_update_status(message.content)

# -------------------------------------
# Flask 웹 API 로직
# -------------------------------------
@app.route('/')
def home():
    """서버가 살아있는지 확인하는 기본 경로"""
    return "디스코드 모니터링 API 서버가 실행 중입니다."

@app.route('/status')
def get_statuses():
    """모든 컴퓨터의 현재 상태를 JSON 형태로 반환합니다."""
    with status_lock:
        # 딕셔너리의 복사본을 반환하여 안전성 확보
        return jsonify(computer_statuses)

# -------------------------------------
# 프로그램 실행
# -------------------------------------
def run_flask():
    """Flask 서버를 별도의 스레드에서 실행합니다."""
    # Railway는 PORT 환경 변수를 자동으로 설정해줍니다.
    port = int(os.environ.get('PORT', 5000))
    # host='0.0.0.0'은 외부에서 접근 가능하도록 설정합니다.
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    if not DISCORD_TOKEN or not TARGET_CHANNEL_ID:
        print("오류: DISCORD_TOKEN 또는 TARGET_CHANNEL_ID 환경 변수가 설정되지 않았습니다.")
    else:
        # Flask 서버를 백그라운드 스레드에서 실행
        flask_thread = threading.Thread(target=run_flask)
        flask_thread.daemon = True
        flask_thread.start()
        
        # 메인 스레드에서 디스코드 봇 실행 (블로킹)
        client.run(DISCORD_TOKEN)