import dateutil.parser, pytz
from datetime import datetime, timedelta

def getTime(addtime):
    to_zone = pytz.timezone('America/Chicago')
    now = datetime.now(to_zone) + timedelta(minutes=addtime) - timedelta(hours=1)
    current_string = now.strftime('%Y-%m-%d %H:%M:%S')

    return current_string

def getRCTime(timestamp):
    last_mod_time = dateutil.parser.parse(timestamp) - timedelta(hours=5)
    last_mod_string = last_mod_time.strftime('%Y-%m-%d %I:%M %p')
    return last_mod_string

def checkTime():
    to_zone = pytz.timezone('America/Chicago')
    now = datetime.now(to_zone)
    current_string = [now.strftime('%Y-%m-%d %H:%M')]
    compare_time = now.strftime('%H')
    if int(compare_time) > 16:
        current_string.append(1)
    else:
        current_string.append(0)
    return current_string
