import dateutil.parser, pytz
from datetime import datetime, timedelta

def isTime(timestamp):
    last_mod_time = dateutil.parser.parse(timestamp)
    last_mod_time -= timedelta(hours=5)
    #date_format_string = last_mod_time.strftime("%Y-%m-%d %H:%M:%S")

    last_mod_newtime = last_mod_time + timedelta(hours=3)


    to_zone = pytz.timezone('America/Chicago')
    now = datetime.now(to_zone)

    last_mod_string = last_mod_newtime.strftime('%Y-%m-%d %H:%M:%S')
    current_string = now.strftime('%Y-%m-%d %H:%M:%S')

    last_mod_date = last_mod_newtime.strftime('%m-%d')
    current_date = now.strftime('%m-%d')

    last_mod_hour = last_mod_newtime.strftime('%H:%M:%S')
    current_hour = now.strftime('%H:%M:%S')

    if (current_date > last_mod_date):
        return 1
    elif (current_hour > last_mod_hour):
        return 1
    else:
        return 0

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

