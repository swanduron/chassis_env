import json

FILE_URL = 'config.json'

data = {
    'ap': '',
    'password': '',
    'temp_low': 0,
    'temp_high': 100,
    'speed_low': 20,
    'speed_high': 95,
    'ntp':'192.168.1.1'
}

with open(FILE_URL, mode='w') as file_target:
    json.dump(data, file_target, indent=2)