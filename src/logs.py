import pytz
from datetime import datetime

def log(text, text2 = None):
    if text2 is not None:
        text += text2
    to_zone = pytz.timezone('America/Chicago')
    now = datetime.now(to_zone)
    new_time = now.strftime("%Y-%d-%m %I:%M %p")
    
    print("{}: {}".format(new_time,text))

    with open("logs.txt","a") as f:
        f.write("{}: {}\n".format(new_time,text))