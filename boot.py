# 開發板接電後立刻執行程式:
# 1. 連接wifi
from wifi import connect_info, connect_wifi

print("開機, 連線Wi-Fi中...")
ssid, password = connect_info()  # 取得Wi-Fi連線資訊供其他函數檔案使用
connect_wifi(ssid, password)  # 使用取得的資訊連線Wi-Fi