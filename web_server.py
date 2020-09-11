from microWebSrv import MicroWebSrv
import network

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan_list = wlan.scan()
wlan_list = [i[0].decode() for i in wlan_list]
wlan.active(False)


for i in wlan_list:
    print(i)

ap = network.WLAN(network.AP_IF)
ap.active(True)
print('ap status>:', ap.ifconfig())
print('ap ssid>:', ap.config('essid'))

# ----------------------------------------------------------------------------

@MicroWebSrv.route('/')
def _httpHandlerTestGet(httpClient, httpResponse):
    select_list = ''

    for wlan_index in range(len(wlan_list)):
        select_list += '<option value="{}">{}</option>'.format(wlan_index, wlan_list[wlan_index])

    content = """<html>
        <head>
            <title>ESP Web Server</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <link rel="icon" href="data:,">
            <style>html{font-family: Helvetica; display:inline-block; margin: 0px auto; text-align: center;}
          h1{color: #0F3376; padding: 2vh;}p{font-size: 1.5rem;}.button{display: inline-block; background-color: #e7bd3b; border: none;
          border-radius: 4px; color: white; padding: 16px 40px; text-decoration: none; font-size: 30px; margin: 2px; cursor: pointer;}
          .button2{background-color: #4286f4;}</style>
        </head>
        <body>
            <h1>Concent Status</h1>
            <p>WIFI state: <strong>NEW</strong></p>
            <p><a href="/?led=on"><button class="button">ON</button></a></p>
            <p><a href="/?led=off"><button class="button button2">OFF</button></a></p>
            <form action="" method="POST">
            WIFI: <select name="wifi">""" + select_list + """</select><br>
            WIFI password: <input type="text" name="password"><br>
            First name: <input type="text" name="fname"><br>
            Last name: <input type="text" name="lname"><br>
            <input type="submit" value="提交">
        </form>
        </body>
        </html>"""
    httpResponse.WriteResponseOk( headers=None,
                                  contentType="text/html",
                                  contentCharset="UTF-8",
                                  content=content)


@MicroWebSrv.route('/', 'POST')
def _httpHandlerTestPost(httpClient, httpResponse) :
    formData  = httpClient.ReadRequestPostedFormData()
    print(formData)
    # fromData = '{'wifi': '14', 'fname': '222', 'password': '111', 'lname': '333'}'
    httpResponse.WriteResponseOk(headers=None,
                                 contentType="text/html",
                                 contentCharset="UTF-8",
                                 content='666')


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