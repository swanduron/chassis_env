from machine import Pin, I2C, PWM, Timer
from time import sleep_ms, ticks_ms, sleep
from esp8266_i2c_lcd import I2cLcd
import ds18x20
import ds3231
import onewire

DEFAULT_I2C_ADDR = 0x27
TEMP_LOW = 20
TEMP_HIGH = 45
SPEED_LOW = 20
SPEED_HIGH = 100
temp = 15

led = Pin(2, Pin.OUT)
led.value(1)

CONFIG_BTN = Pin(34, Pin.IN)

i2c = I2C(scl=Pin(22), sda=Pin(21), freq=400000)
real_clock = ds3231.DS3231(i2c)
ds_sensor = ds18x20.DS18X20(onewire.OneWire(Pin(4)))
ds_dev = ds_sensor.scan()[0]

lcd = I2cLcd(i2c, DEFAULT_I2C_ADDR, 2, 16)

if CONFIG_BTN.value()==0:
    lcd.putstr('Config mode')
    sleep(0.5)
    import web_server
else:
    lcd.putstr("Temp control\nStart online!")

fan1 = PWM(Pin(5))
fan2 = PWM(Pin(18))
fan3 = PWM(Pin(19))
fan1.freq(25000)
fan2.freq(25000)
fan3.freq(25000)
fan_matrix = [fan1, fan2, fan3]


def fan_operation(fan_list, speed_value):
    for fan in fan_list:
        fan.duty(speed_value)


def temp_detect(timer):
    global temp
    led.value(0 if led.value() else 1)
    ds_sensor.convert_temp()
    sleep_ms(350)
    temp = ds_sensor.read_temp(ds_dev)


temp_timer = Timer(1)
temp_timer.init(period=1000, mode=Timer.PERIODIC, callback=temp_detect)


def speed_change(timer):

    percent = (temp - TEMP_LOW) / (TEMP_HIGH - TEMP_LOW)
    if percent < 0:
        percent = 0
    elif percent > 1:
        percent = 1
    speed_diff = ((SPEED_HIGH - SPEED_LOW) * percent + SPEED_LOW) / 100
    fan_operation(fan_matrix, int(1023 * speed_diff))


temp_timer = Timer(2)
temp_timer.init(period=500, mode=Timer.PERIODIC, callback=speed_change)


def z_fill(string, position='left', length=4, tag='0'):

    string = str(string)
    if len(string) >= length:
        return string
    else:

        if position == 'left':
            for i in range(length - len(string)):
                string = tag + string
            return string
        else:
            for i in range(length - len(string)):
                string = string + tag
            return string


def put_info():
    year, month, day = real_clock.Date()
    hour, minute, second = real_clock.Time()
    date = [z_fill(i, length=2) for i in [year, month, day]]
    times = [z_fill(i, length=2) for i in [hour, minute, second]]
    string_buffer = '-'.join(date) + ' ' + ':'.join(times)
    time = string_buffer[:16]
    duty_value = fan1.duty()
    string_buffer = 'PWM:' + z_fill(duty_value) + ' T:' + str(temp)
    pwm = string_buffer[:16]
    lcd.move_to(0, 0)
    lcd.putstr(time + pwm)


# Enable IRQ for system fresh caused by DS3231
Pin(25, Pin.IN).irq(trigger=Pin.IRQ_FALLING, handler=put_info)

# need to be removed when DS trigger is existed.
while True:
    put_info()
    sleep(1)