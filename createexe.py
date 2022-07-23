import PyInstaller.__main__
import time
from src.credentials import client_secret
#noconsole:
#   python3 -m PyInstaller --noconsole --onefile --clean --icon=Logo_b.ico --add-data "Logo_b.ico;." main.py
#console:
#   python3 -m PyInstaller --onefile --clean --icon=Logo_b.ico --add-data "assets/Logo_b.ico;." main.py -n cmtmgr

version = "3.26"
debug = 0
getver = version.split('.')
noconsole = 1


if debug == 1:
    getver.append("beta")
if noconsole == 0:
    getver.append("dev")

console = [
    'SFpull.py',
    '--onefile',
    '--clean',
    '--icon=logo.ico',
    '--add-data=logo.ico;.',
    '--key={}'.format(client_secret),
    '--name=cmtmgr_{}'.format("_".join(getver))
]

print("Creating {}".format(console[5]))

if noconsole == 1:
    console.append('--noconsole')
    print(console[6])

time.sleep(5)

PyInstaller.__main__.run(console)