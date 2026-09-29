# 目標: 控制開發板wifi晶片連接路由器(*:代表可調整之重要參數)
# 1. 建立 WLAN 終端模式物件 ok
# 2. 啟用 WLAN 介面 ok
# 3. 呼叫 connect 傳入 Wi-Fi 帳密 ok
# 4. 用 while 迴圈持續檢查 isconnected() 是否為 True ok
# 5. 連線成功後，印出 ifconfig() 取出的 IP 資訊 ok
import network
import time
import json
# from blink import Led_Blink
wlan = network.WLAN(network.STA_IF)  # STA_IF: WIFI用戶端模式(搜尋WIFI訊號)
# print("連線狀態:", wlan.isconnected())

def scan_wifi():
    wlan.active(True)   # 啟用WIFI介面
    # 掃描附近的WIFI訊號, 回傳值:(SSID, BSSID-MAC位址, channel, RSSI-訊號強度, security-認證編號, hidden)
    wifi_info = wlan.scan()
    w_count = 1
    # print("full wifi data:", wifi_info) 
    for wifi_ssid in wifi_info:
        if wifi_ssid[0] == b"":  # 過濾掉空字串的SSID名
            continue
        # 格式化寫法: %d(整數), %s(字串), %f(浮點數) + %變數
        print("wifi_ssid %d:" % w_count, wifi_ssid[0].decode()) # 印出附近的WIFI訊號名
        w_count += 1

# 取得Wi-Fi連線資訊供其他函數檔案使用(*改wifi名稱,密碼調整這邊函數即可)
def connect_info():
    with open('pc-lan.json','r') as pc_info:
        pc = json.load(pc_info) # 讀取json檔案並轉換成"dict"型別
        wifi_name = pc.get('ssid') # *wifi名更換
        wifi_code = pc.get('password') # *wifi密碼更換
        # print("wifi_name:", wifi_name)
        # print("wifi_code:", wifi_code)
    return wifi_name, wifi_code

def connect_wifi(ssid, password):
    wlan.active(True)  # 啟用WIFI介面
    wlan.disconnect() # 重置上次連線狀態(1秒)
    time.sleep(1)

    t_wait = 10  # 設置連線閒置時間計數器:10秒

    if not wlan.isconnected():  # 初次檢查是否連線(省略刷新程式碼時重複連線)
        print("Connecting to WiFi...")
        wlan.connect(ssid, password)  # 傳入Wi-Fi帳密連線
        while not wlan.isconnected():  # 持續檢查是否連線成功
            # machine.idle()  # 等待連線成功(閒置)
            # 設置超時機制，避免無限等待
            time.sleep(1) # 延遲1s後給倒數計數器:-1 
            t_wait -= 1
            if t_wait <= 0:
                print("WiFi連接失敗. 請檢查輸入資訊.")
                wlan.disconnect()  # 倒數超時後斷開連線
                return not wlan.isconnected()# 結束函數執行並回傳狀態"未連線"
    print("WiFi連接成功!")
    print("Wifi Name:", wlan.config('ssid'))  # 印出Wi-Fi名稱
    print("IP Address:", wlan.ifconfig()[0])  # 印出IP資訊(回傳值:IP, Subnet Mask, Gateway, DNS)
    return wlan.isconnected


# --------執行區--------- #
# scan_wifi()
# connect_wifi("Xperia_4899", "sharenet256893")  # 替換Wi-Fi帳密
# ssid, password = connect_info()  # 取得Wi-Fi連線資訊供其他函數檔案使用
# # connect_wifi(ssid, password)  # 使用取得的資訊連線Wi-Fi
# print("ssid:", ssid)
