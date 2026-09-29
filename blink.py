from machine import Pin
from utime import sleep
import network

# 2: esp32上LED燈引腳編號(D2)/pin.out()表示輸出模式
def Led_Blink():
    pin = Pin(2, Pin.OUT)
    wlan = network.WLAN(network.STA_IF)
    print("LED starts flashing...")

    while True:  # 持續檢查是否連線成功
        try:
            pin.toggle() # 切換LED狀態(點滅)
            sleep(1) # sleep 1sec
        except KeyboardInterrupt:
            break
    pin.off()
    
    print("Finished.")
