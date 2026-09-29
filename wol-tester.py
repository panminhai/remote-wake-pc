import socket

# 建立 UDP 監聽節點
listener = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# 允許通訊埠重用
listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# 綁定監聽本機的所有 IP 與 Port 9
listener.bind(('0.0.0.0', 9))

print("UDP 監聽器已啟動，正在等待 WOL 封包...")

# 阻塞等待接收資料（預設最大接收 1024 bytes）
data, addr = listener.recvfrom(1024)

print("\n收到封包了！")
print(f"來源位址: {addr}")
print(f"封包大小: {len(data)} 位元組")
print("封包內容:", data)

listener.close()