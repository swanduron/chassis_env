from microWebSrv import MicroWebSrv
import network
from time import sleep_ms, ticks_ms, sleep
from machine import Pin, I2C, PWM, Timer
from esp8266_i2c_lcd import I2cLcd
import json

DEFAULT_I2C_ADDR = 0x27
i2c = I2C(scl=Pin(22), sda=Pin(21), freq=400000)
lcd = I2cLcd(i2c, DEFAULT_I2C_ADDR, 2, 16)



wlan = network.WLAN(network.STA_IF)

ap = network.WLAN(network.AP_IF)
ap.active(True)
print('ap status>:', ap.ifconfig())
print('ap ssid>:', ap.config('essid'))
lcd.putstr("IP: %s\nSD: %s!" % (ap.ifconfig()[0],ap.config('essid')))


with open('config.json') as save_obj:
    saved_info = json.load(save_obj)
    ap = saved_info.get('ap')
    password = saved_info.get('password')
    temp_low = saved_info.get('temp_low')
    temp_high = saved_info.get('temp_high')
    speed_low = saved_info.get('speed_low')
    speed_high = saved_info.get('speed_high')
    ntp = saved_info.get('ntp')

# ----------------------------------------------------------------------------

@MicroWebSrv.route('/')
def _httpHandlerTestGet(httpClient, httpResponse):
    select_list = ''
    wlan.active(True)
    sleep(1)
    wlan_list = wlan.scan()
    wlan_list = [i[0].decode() for i in wlan_list]
    wlan.active(False)

    for wlan_index in range(len(wlan_list)):
        select_list += '<option value="{}">{}</option>'.format(wlan_list[wlan_index], wlan_list[wlan_index])

    content = """<!DOCTYPE html>
    <html>
        <head>
            <title>ESP Web Server</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>html{font-family: Helvetica; display:inline-block; margin: 0px auto; text-align: center;}</style>
        </head>
        <body>
            <h1>Config Page</h1>
            <p>WIFI state: <strong>NEW</strong></p>
            Currect Configuration
            <hr>
            AP name:%s<br>
            AP password: %s<br>
            Temp: high_level %s, low_level %s<br>
            Speed: high_level %s, low_level %s<br>
            NTP server: %s<br>
            <hr> 
            <form action="" method="POST">
                WIFI: <select name="ap">%s</select><br>
                WIFI password: <input type="text" name="password"><br>
                Temp: high_level: <select name="temp_high" id="temp_high"></select> , low_level:<select name="temp_low" id="temp_low"></select><br>
                Speed: high_level:<select name="speed_high" id="speed_high"></select>, low_level:<select name="speed_low" id="speed_low"></select><br>
                NTP server: <input type="text" name="ntp"><br>
                <input type="submit" value="提交">
            </form>
        </body>
        <script>
            var id_list = ["temp_high","temp_low","speed_high","speed_low"]
            window.addEventListener('load', () => {
                for (x=0; x<id_list.length; x++){
                    id_name = id_list[x];
                    var selectAge = document.getElementById(id_name);
                    for(let i = 1; i<=100; i++) {
                        let option = document.createElement('option');
                        option.innerText = i;
                        selectAge.appendChild(option);
                    }
                }
            })
        </script>
        </html>""" % (ap, password, temp_high, temp_low, speed_high, speed_low, ntp, select_list)
    httpResponse.WriteResponseOk( headers=None,
                                  contentType="text/html",
                                  contentCharset="UTF-8",
                                  content=content)


@MicroWebSrv.route('/', 'POST')
def _httpHandlerTestPost(httpClient, httpResponse) :
    wrong_field = []
    formData  = httpClient.ReadRequestPostedFormData()
    print(formData)
    # fromData = '{'wifi': '14', 'fname': '222', 'password': '111', 'lname': '333'}'

    ap = formData['ap']
    password = formData['password']
    ntp = formData['ntp']
    speed_low = int(formData['speed_low'])
    speed_high = int(formData['speed_high'])
    temp_low = int(formData['temp_low'])
    temp_high = int(formData['temp_high'])

    content = """<!DOCTYPE html>
        <html>
            <head>
                <title>ESP Web Server</title>
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <style>html{font-family: Helvetica; display:inline-block; margin: 0px auto; text-align: center;}</style>
            </head>
            <body>
                <h1>Config result</h1>
                <p>WIFI state: <strong>NEW</strong></p>
                Currect Configuration
                <hr>
                AP name:%s<br>
                AP password: %s<br>
                Temp: high_level %s, low_level %s<br>
                Speed: high_level %s, low_level %s<br>
                NTP server: %s<br>
                <hr>
                <h2>Your config has been saved!</h2>
                <h2>System will reboot automatic in 5 second.</h2>
                <h2>Or you can flap power manually.</h2>
            </body>
        </html>""" % (ap, password, temp_high, temp_low, speed_high, speed_low, ntp)
    data = {
        'ap': ap,
        'password': password,
        'temp_low': temp_low,
        'temp_high': temp_high,
        'speed_low': speed_low,
        'speed_high': speed_high,
        'ntp': ntp
    }
    with open('config.json', mode='w') as file_obj:
        json.dump(data, file_obj)
    httpResponse.WriteResponseOk(headers=None,
                                 contentType="text/html",
                                 contentCharset="UTF-8",
                                 content=content)


def _acceptWebSocketCallback(webSocket, httpClient) :
    print("WS ACCEPT")
    webSocket.RecvTextCallback   = _recvTextCallback
    webSocket.RecvBinaryCallback = _recvBinaryCallback
    webSocket.ClosedCallback 	 = _closedCallback

def _recvTextCallback(webSocket, msg) :
    print("WS RECV TEXT : %s" % msg)
    webSocket.SendText("Reply for %s" % msg)

def _recvBinaryCallback(webSocket, data) :
    print("WS RECV DATA : %s" % data)

def _closedCallback(webSocket) :
    print("WS CLOSED")

srv = MicroWebSrv(webPath='www/')
srv.MaxWebSocketRecvLen = 256
srv.WebSocketThreaded = False
srv.AcceptWebSocketCallback = _acceptWebSocketCallback
srv.Start()