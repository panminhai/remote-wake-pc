# 目標:驅動連網後整個專案功能
# 1. 設置MQTT連線參數  ok
# 2. 設置MQTT監聽主題(topic)與接收訊息的callback函數 ok
# 3. 透過mqtt-subscribe監控Adafruit IO平台帳號(Feed: remote-pc-command):while迴圈 ok
# 4. 把監聽收到的指定訊息(!wakepc)驅動wol.py檢查&發送封包 ok
# 預定: 改善長時間check_msg閒置時會解除mqtt連線的問題
from wifi import connect_info, connect_wifi
from umqtt.simple import MQTTClient # 電腦本機python沒有裝MicroPython套件, 無視錯誤即可
from wol import mac_check, mac_to_bytes, send_wol_packet, mac_info
import network
import time
import json


mqtt_server = "io.adafruit.com" # Adafruit IO平台位址
mqtt_port = 1883 # Adafruit IO平台port
mqtt_id = "esp32_1" # 設備名(預定: 動態調整名稱讓每次連線都可以以乾淨狀態開始)

# 取出json檔紀錄的broker(adafruit IO)用戶情報
with open('pc-lan.json', 'r') as pc_info:
    pc = json.load(pc_info)
    mqtt_name = pc.get('aio_username') # Adafruit IO 用戶名
    mqtt_password = pc.get('aio_key') # Adafruit IO 用戶金鑰
    mqtt_topic = pc.get('aio_topic') # Topic:MQTT通訊協定中用來標示、分類與路由訊息的字串地址(在這裡是feed位址)
    # print(f"用戶名:{mqtt_name} \n金鑰:{mqtt_password} \n用戶主題:{mqtt_topic}")

# MQTTClient參數(client_id, server, port=0, user=None, password=None, keepalive=0(連線存活時間(秒)), ssl=False, ssl_params={})
mqtt = MQTTClient(client_id=mqtt_id, server=mqtt_server, port=mqtt_port, user=mqtt_name, password=mqtt_password, keepalive=60) 
# mqtt_topic = "pan_1331/feeds/remote-pc-command" # Topic:MQTT通訊協定中用來標示、分類與路由訊息的字串地址(在這裡是feed位址)


#-------函式區-------#
def send_to_wol(topic, message):
    text_content = message.decode() # 將bytes型別轉換成str型別
    

    if text_content == "!wakepc":
        print(f"收到指令: {text_content}, 將執行wol.py發送封包...")
        mac_addr = mac_info() # 取得MAC位址

        # 只有驗證過的MAC位址才能發送wol封包
        if not mac_check(mac_addr):
            print("MAC驗證未通過, 請檢查正確格式")
            
        else:
            # 發送WOL流程
            valid_addr = mac_check(mac_addr)
            ready_wol = mac_to_bytes(valid_addr)
            send_result = send_wol_packet(ready_wol)
            # print(f"發送結果:{send_result}")

            if send_result:
                print("WOL封包已發送!")
    else:
        # 有時間的話做成回復discord訊息("無效的指令"之類的)
        print("無效的指令...")

def main():
    wlan = network.WLAN(network.STA_IF)
    mqtt.set_callback(send_to_wol) # 設定接收訊息的callback函數
    mqtt_isconnected = False # 設置mqtt連線狀態(初始:false)
    start_time = time.time() # 設置時間節點(初始:當下時間)
    while True:
        #------初次連線/異常處理區------#
        # 確認wifi連線
        if not wlan.isconnected():
            print("WiFi連線中斷,將再次重新連線...")
            ssid, password = connect_info() # 取得Wi-Fi連線資訊
            connect_wifi(ssid, password) # wifi連線
            mqtt_isconnected = False # Wi-Fi中途如果斷線，標記 MQTT 需重連
        # 確認mqtt連線
        if not mqtt_isconnected:
            try:
                print("開始連線MQTT...")
                mqtt.connect() # mqtt連線
                mqtt.subscribe(mqtt_topic)
                mqtt_isconnected = True
                time.sleep(1.5)
                print("監聽中...")

            except Exception as e:
                print("mqtt連線異常, 再次重新連線...", e)
                time.sleep(5)
                continue

            # 手動停止程式處理
            except KeyboardInterrupt:
                print("程式手動中斷, 將斷開連線...")
                try:
                    wlan.disconnect() # 斷線
                    wlan.active(False) # 關閉WIFI介面
                except Exception as e:
                    print("無視wifi異常繼續執行斷線...", e)
                    pass
                print("連線已中斷, 結束程式...")
                break

        #------mqtt通訊監聽區------#
        try:
            time.sleep(1) # 延遲點:避免esp32過度運作
            # 持續檢查該主題是否有訊息傳入(*wait_msg:會卡住程式, 直到有訊息傳入後才繼續執行所以不用)
            mqtt.check_msg() 
        except Exception as e:
            print("監聽時發生錯誤,將重新連接...", e)
            mqtt_isconnected = False
            # 注意: 在 except 內部裡面發生的新錯誤，無法被外層的 try 攔截 
            try:
                mqtt.disconnect() # 斷線
            except:
                # 防範其他連線發生錯誤:預防wifi斷線時mqtt也斷線, 造成mqtt.disconnect()報錯
                pass
            time.sleep(5) # 延遲點:避免CPU過度運作,5秒後回到迴圈重來

        except KeyboardInterrupt:
            mqtt_isconnected = False
            print("程式手動中斷, 將斷開連線...")
            try:
                mqtt.disconnect() # mqtt斷線
            except Exception as e:
                print("無視mqtt異常繼續執行斷線...", e)
                pass

            try:
                wlan.disconnect() # mqtt斷線
                wlan.active(False) # 關閉WIFI介面
            except Exception as e:
                print("無視wifi異常繼續執行斷線...", e)
                pass
            print("連線已中斷, 結束程式...")
            break
        # 每隔30秒後傳送一次ping訊號, 避免長時間閒置導致mqtt斷線
        if time.time() - start_time > 30:
            try:
                mqtt.ping() # 發送ping訊號
                start_time = time.time() # 重置時間節點
                # print("發送ping心跳包...")
            except Exception as e:
                print("傳送ping時發生錯誤, 將重新連接...", e)
                mqtt_isconnected = False
                # 注意: 在 except 內部裡面發生的新錯誤，無法被外層的 try 攔截 
                try:
                    mqtt.disconnect() # 斷線
                except:
                    # 防範其他連線發生錯誤:預防wifi斷線時mqtt也斷線, 造成mqtt.disconnect()報錯
                    pass
                time.sleep(5) # 延遲點:避免CPU過度運作,5秒後回到迴圈重來
                
#-------程式執行區-------#
if __name__ == "__main__":
    main()