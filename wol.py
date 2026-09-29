# 目標:對指定電腦發送Wake-on-LAN封包訊號(mac位址編碼轉換→建立socket→發送封包訊號→關閉socket)
# 1. 取得目標電腦的MAC位址(notepc:28:D0:43:0A:3E:54) ok
# 2. 將MAC位址轉換成16進位字串(去除冒號) + 轉換成位元組 ok
# 3. 建立WOL封包訊號: FF FF FF FF FF FF + MAC位址重複16次 ok
# 4. 建立UDP socket物件發送 ok

# print(repr(mac_addr)) # 印出原始MAC位址(包含引號)
# print(len(mac_addr)) # 印出MAC位址長度(字元數)
# 正規表達式: r"^(...)$", []:匹配任意字符, {n}:匹配n個字符, ():分組
# 表達式(addr_check): ^:字串開頭, $:字串結束, {2}:匹配恰好2個字符, [:-]:匹配冒號或連字符, {5}:匹配恰好5個字符
# addr_check = re.match(r"^([0-9a-fA-F][0-9a-fA-F][:-])([0-9a-fA-F][0-9a-fA-F][:-])([0-9a-fA-F][0-9a-fA-F][:-])([0-9a-fA-F][0-9a-fA-F][:-])([0-9a-fA-F][0-9a-fA-F][:-])([0-9a-fA-F][0-9a-fA-F])$", mac_addr) # 檢查MAC位址格式是否正確
# 輸入MAC位址(手動)
# mac_addr = input("請輸入目標電腦的MAC位址(格式:6組雙位數):").strip()  # 去除前後空白字元
# addr_check = mac_addr.split(':')  # 將MAC位址以冒號分割成字串陣列(list)
# print("MAC位址分割結果:", addr_check) # 印出分割後的MAC位址陣列(去除中括號)

import socket # 建立網路通訊節點(伺服器/客戶端...)
import binascii # 16 進位字串與位元組(電腦讀取用)的轉換處理
import json
# import re # 在micropico裡表達式無法讀取大括號:{}



# --------函數區--------- #

# 取得設備MAC資訊供其他函式使用
def mac_info():
    # 打開json檔案並用讀取模式(with用意: 程序結束會自動釋放資源,省略多餘處理-close)
    with open('pc-lan.json','r') as pc_info:
        mac = json.load(pc_info) # 讀取json檔案並轉換成"dict"型別
        mac_name = mac.get('mac_wire')
        # print(f'設備名稱:{mac_name}')
    return mac_name


# MAC位址格式檢查
def mac_check(data_check):
    # MAC數列分隔符號轉換(― →：)並依序分割成字串陣列(list) *如果位址數列是"-"分隔的話
    check_addr = data_check.replace('-',':').split(':') 

    # --------防線設置1--------- #
    if len(check_addr) != 6: # 檢查MAC位址是否是6組數
        print("MAC位址格式錯誤:必須是6組數")
        return False


    # --------防線設置2--------- #
    # len: mac位址串列長度(6組)
    for i in range(len(check_addr)):
        # print("檢查前:", data_check[i])
        if len(check_addr[i]) != 2: # 檢查MAC每組數是否是2位數
            print("MAC位址格式錯誤:每組數必須是2位數")
            return False

        try:
            int(check_addr[i], 16) # 嘗試將每組16進位數組轉換成10進位
            
        except ValueError:
            print("MAC位址格式錯誤:每組數必須是16進位數字")
            return False
            
    return check_addr
    

# 轉換:MAC位址→位元組→wol封包訊號
def mac_to_bytes(addr_checked):
    
    mac_string = ''.join(addr_checked) # 將MAC位址陣列轉換成單一字串
    mac_bytes = binascii.unhexlify(mac_string) # 將MAC位址轉換成位元組
    print("位元組mac位址:", mac_bytes) # 印出位元組
    # 建立WOL封包訊號: 0xFF:重複6次(喚醒PC網卡電路) + MAC位址:重複16次(比對數次成功後向主機板發送開機訊號)
    wol_packet = b'\xff'*6 + mac_bytes*16
    wol_len = len(wol_packet)
    print(f"封包整體長度:{wol_len}位元組")
    print("WOL封包訊號:", wol_packet) # 印出WOL封包訊號
    return wol_packet # 回傳WOL封包訊號(發送喚醒訊號用)


def send_wol_packet(wol_signal):
    pc_addr = "255.255.255.255" # ip位址:全域廣播(有被路由器封鎖的風險)
    udp_port = 9 # 設置udp接口
    # 建立UDP socket物件, 參數:AF_INET:IPv4, SOCK_DGRAM:UDP
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    try:
        # 設置通訊端屬性權限, 參數: SOL_SOCKET:通用層級(level), SO_BROADCAST:廣播封包(optname), 1: 開啟
        udp.setsockopt(socket.SOL_SOCKET,socket.SO_BROADCAST, 1)
        # 設置封包發送目標, 參數:封包訊號, (目標IP位址, 目標UDP接口)
        udp.sendto(wol_signal, (pc_addr, udp_port))
        print("sending wol...")
    except Exception as e:
        print("封包傳送失誤:", e)
        return False
    finally:
        udp.close()
    return True
    
    
# --------執行區--------- #

# check_result = mac_check(addr_check)

# if not check_result:
#     print("mac位址驗證失敗, 請重新輸入...")
# else:
#     valid_addr = check_result
#     ready_wol = mac_to_bytes(valid_addr) # 呼叫函式將MAC位址轉換成位元組
#     send_wol_packet(ready_wol) # 呼叫函式發送WOL封包訊號
# name = mac_info()
# print("設備名稱結果是:", name)
