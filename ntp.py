import usocket as socket
import ustruct as struct

import time
import network

from machine import Pin, I2C
import ssd1306

i2c = I2C(scl=Pin(5), sda=Pin(4), freq=100000)

lcd = ssd1306.SSD1306_I2C(128, 64, i2c)

NTP_DELTA = 3155673600

host = "cn.pool.ntp.org"  # 国内的NTP时间服务器

SSID = "yourssid"
PASSWORD = "yourpassword"
wlan = None
s = None


def connectWifi(ssid, passwd):
    global wlan
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.disconnect()
    wlan.connect(ssid, passwd)
    while (wlan.ifconfig()[0] == '0.0.0.0'):
        time.sleep(1)
    return True


connectWifi(SSID, PASSWORD)


def time():
    NTP_QUERY = bytearray(48)
    NTP_QUERY[0] = 0x1b
    addr = socket.getaddrinfo(host, 123)[0][-1]
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(1)
    res = s.sendto(NTP_QUERY, addr)
    msg = s.recv(48)
    s.close()
    val = struct.unpack("!I", msg[40:44])[0]
    return val - NTP_DELTA


if __name__ == '__main__':
    t = time()
    import utime

    tm = utime.localtime(t)
    tm = tm[0:3] + (0,) + tm[3:6] + (0,)
    print(tm)
    year = tm[0]
    print(year)
    mouth = tm[1]
    day = tm[2]
    hour = tm[4]
    sencod = tm[6]
    if 16 <= hour < 24:  # ntp授时获取的是格林尼治时间 这里我们转换为我们东8区的时间
        day = day + 1
    hour = hour + 8
    min = tm[5]
    if hour > 24:
        hour = hour - 24
    print(mouth)
    print(day)
    print(hour)
    print(min)
    print(sencod)