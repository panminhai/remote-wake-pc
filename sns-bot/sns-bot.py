# 目標: 處理discord聊天Bot的訊息並利用mqtt通訊讓Adafruit IO接收
# 1. 各金鑰,密碼等重要資訊配置(設置.env檔案) ok
# 建立discord BOT: ok
# 2. 初始化 discord.Client 
# 3. 開啟: Intents.default & message_content函式權限 
# 4. 和discord BOT連線後報備(事件:on ready)
# 5. 防呆設置: 過濾訊息(避免讀取到機器人本身發出的訊息) 
# 6. 訊息比對: if message.content == '!wakepc':指令是否被讀取 
# 撰寫 Adafruit IO(broker) 指令上傳函式: ok
# 7. 從env檔取得broker連線資訊
# 8. 設置post資料(broker後臺驗證金鑰, 欲傳送指令:!wakepc, broker後臺網址)
# 9. 用變數接post的回應(response)
# 10. 確認回應結果是否皆擷取到(try/except)
import discord as ds
import requests as rq
import os
from dotenv import load_dotenv
import re

# 設置discord的功能並總結成啟用開關
intents = ds.Intents.default()
# 啟用: discord接收訊息做使用的功能
intents.message_content = True 

client = ds.Client(intents=intents) # 初始化discord.Client(和discord連線)
# 從.env檔案讀取變數並設定到 os.environ 中(需額外裝 "os"模組來取得資料)
load_dotenv("sns-bot/mqtt-info.env")# 參數:env檔案位址
#------函式區------#

# 將訊息傳給mqtt的伺服器端(adafruit IO)
def send_to_broker(command):
    broker_name = os.getenv('AIO_USERNAME')
    broker_feed = os.getenv('AIO_FEED')
    broker_key = os.getenv('AIO_KEY')
    # print(f"指令是:{command}")
    # REST API 網址(進入網頁後端填資料用)格式: 主網址+/api/v2/<AIO用戶名>/feeds/<Feed Key:去feed總列表找>/data:讓伺服器知道要寫入資料
    url = f"https://io.adafruit.com/api/v2/{broker_name}/feeds/{broker_feed}/data"
    # header_id: 用來進入adafruit IO帳號的通行證(aio金鑰) X-AIO-Key: 官方指定設置欄位名
    header_id = {
        "X-AIO-Key":broker_key,
        "Content-Type": "application/json"
    } # Content-Type: 設置要傳給伺服器的資料格式:json
    # body: 設置給adafruit IO接收資料的內文("value"為預設欄位名)
    body = {
        "value":command
    }
    try:
        response = rq.post(url, headers=header_id, json=body, timeout=5)
        print(f"欲前往網站: {url}")
        # response = rq.get(post_response) # 錯誤:不管是GET或POST, 在處理後都會回傳Response 物件, 只需用變數去接即可
        if response.status_code == 200 or response.status_code == 201:
            print(f"已上傳指令:{command}")
            return True
        elif response.status_code == 401:
            print("ADAFRUIT IO權限驗證錯誤!")
            return False
        elif response.status_code == 404:
            print("ADAFRUIT IO資料不存在錯誤!")
            return False
        else:
            print(f"ADAFRUIT IO指令發生預料外情況未能送達!狀態碼:{response.status_code}")
    except Exception as e: 
        print("發送指令途中遭遇連線錯誤...", e)
        return False


# client.event: 負責和discord.py模組連線把事件函式回傳
@client.event
# on_ready: 連線成功事件,確認連上Bot後報通知
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
# on_message: 接收從discord聊天室那邊形成的訊息的事件
async def on_message(message):
    # 防呆: 過濾訊息(避免讀取到bot帳號本身發出的訊息): 發生後直接終結函式
    if message.author == client.user:
        return
    # 監聽聊天室讀取的訊息 r"^(...)$"
    if message.content.startswith("!"):
        if message.content.startswith("!wakepc"):
            wake_command = "!wakepc"
            await message.channel.send("收到, 執行喚醒桌電程序...")
            send_to_broker(wake_command)
    else:
        
        await message.channel.send("無效的命令, 請再重新輸入...")

#------程式執行區------#
ds_token = os.getenv('DISCORD_TOKEN')
# os.getenv會回傳:字串or空值(None), 為避免傳進空值導致執行崩潰, 需建立判別式
if not ds_token:
    print("權杖內部資料空值或錯誤!請檢查...")
else:
    # 啟用Bot(聊天室狀態進入線上)
    client.run(ds_token)

