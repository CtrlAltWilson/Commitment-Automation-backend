# -*- coding: utf-8 -*-

from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QTimer,QThreadPool
from gui import *

from cryptography.fernet import Fernet
import requests, json,time
from simple_salesforce import Salesforce

try:
    from src.httpstatus import getRequest
    from src.updatecase import updatecase
    from src.constrants import newQuery,testQuery,getQuery,getSupportQuery,getFilteredSupportQuery
    from src.caseQuery import caseQuery
    from src.phone import getPhone
    from src.sf_time import isTime, checkTime
    from src.rc import getAgents,createCommit, getCommits,deleteCommit
    from src.togglecheck import togglecheck, checkautorun
    from src.credentials import \
        client_id,              \
        client_secret,          \
        cm_user,                \
        cm_pass,                \
        access_token,           \
        auth_url
except:
    from httpstatus import getRequest
    from updatecase import updatecase
    from constrants import newQuery, testQuery,getQuery,getSupportQuery,getFilteredSupportQuery
    from caseQuery import caseQuery
    from phone import getPhone
    from sf_time import isTime, checkTime
    from togglecheck import togglecheck, checkautorun
    from rc import getAgents, createCommit, getCommits,deleteCommit
    from credentials import     \
        client_id,              \
        client_secret,          \
        cm_user,                \
        cm_pass,                \
        access_token,           \
        auth_url

query = getFilteredSupportQuery
currentCases = None
globsf = []
commitscreated = 0
stopped = 0
start = 0
th = None
blacklist = ["delet","delete","remove","remov"]
starttime = time.time()
maintimer = None
f_key = Fernet.generate_key()
fern = Fernet(f_key)

def main():
    global globsf,commitscreated, starttime

    recent_update = checkTime() 
    if recent_update[1] == 1:
        stopandclear()
    if stopped == 1:
        return
    if getRequest(auth_url,client_id,client_secret,cm_user,cm_pass,access_token) != 200:
        print("Error accessing database")
        return

    session = requests.Session()
    
    if stopped == 1: return
    
    try:
        sf = Salesforce(username=cm_user,password=cm_pass,security_token=access_token,client_id=client_id,session=session)
    except Exception as e:
        if "INVALID_LOGIN" in str(e):
            print("Incorrect credentials")
    #desc = sf.Account.describe()
    #field_names=[field['name'] for field in desc['fields']]

    #SELECT Id,AccountId,CaseNumber,ContactId,Description,OwnerId,PHone__c,Status,Dialer_Status__c,Sub_Category__c FROM Case WHERE Status = 'Waiting Call Back - 1st Attempt' AND Dialer_Status__c = '{global:RecordStatus}' AND At_Dialer__c = FALSE LIMIT {global:recordlimit}

    sf_data = caseQuery(sf,query)

    records = sf_data['records']

    packaged_case = []
    cases = []
    globsf = []
    bword = None
    if stopped == 1: return

    for record in records:
        
        if stopped == 1: return

        isNew = 0
        appendcase = 0
        phone = getPhone(record['SuppliedPhone'], record['ContactPhone'])
        castime = isTime(record['LastModifiedDate'])
        description = record['Description'].casefold()
        subject = record['Subject'].casefold()
        for word in blacklist:
            if word in description or word in subject:
                appendcase = 1
                bword = word
        if record['Status'] == 'New':
            isNew = 1
        if phone == 0:
            print("{} has no number!".format(record['CaseNumber']))
        if appendcase == 1:
            print("{} has a blacklisted word: {}".format(record['CaseNumber'],bword))
        if phone != 0 and appendcase == 0:
            cases.append([record['CaseNumber'],record['SuppliedName'],record['Platform__c'],record['LastModifiedDate'],castime,phone,isNew,record])
            globsf.append(record['CaseNumber'])

    if stopped == 1: return

    agents = getAgents(fern)
    packaged_case.append(cases)
    packaged_case.append(agents[1])
    packaged_case.append(sf)
    #cases.append(agents)
    #cases.append(sf)
    ui.num_agents.display(agents[1])

    if stopped == 1: return
    commcount = createCommit(packaged_case,fern)
    commitscreated += commcount
    ui.num_commits.display(commitscreated)
    addtoList()

    recent_update = checkTime() 
    ui.label_update_time.setText(recent_update[0])
    if stopped == 1: return

def logs(text):
    with open('logs.txt','w') as f:
        f.write(text)

def timeAlert(text):
    ui.label_alert.setText(text)
    ui.label_alert.repaint()
    deltimer.start(3000)

def addtoList():
    print("getting commits")
    commits = getCommits(fern)
    agents = getAgents(fern)
    ui.list_commitments.clearSelection()
    ui.list_agents.clearSelection()
    ui.list_commitments.clear()
    ui.list_agents.clear()
    if commits != 0 or commits != []:
        for i in range(len(commits)):
            QtWidgets.QListWidgetItem(
                "{}\t{}\t{}".format(commits[i][0],commits[i][2],commits[i][1]),
                ui.list_commitments
            )
        ui.num_queue.display(ui.list_commitments.count())
    for agent in agents[0]:
        QtWidgets.QListWidgetItem(
            "{}".format(agent),
            ui.list_agents
        )
    ui.num_agents.display(agents[1])

def deletefromlist(fern):
    try:
        selected = ui.list_commitments.currentItem().text()
        selected = selected.split("\t")
        deleteCommit(selected[0],fern)
        addtoList()
    except:
        print("Nothing to delete!")
        ui.label_delete_alert.setText("Nothing\nto delete!")
        ui.label_delete_alert.repaint()
        deltimer.start(1000)

def delete_alert():
    ui.label_delete_alert.clear()
    ui.label_alert.clear()
    deltimer.stop()

def stopandclear():
    global stopped, start
    stopped = 1
    start = 0
    ui.label_delete_alert.clear()

def threadworker():
    global stopped
    if start == 1:
        stopped = 0
        QThreadPool.globalInstance().start(main)


def threadbuffer():
    global maintimer, start
    print("Starting")
    recent_update = checkTime()
    if recent_update[1] == 1:
        timeAlert("It's past 4PM! No more commits will be created!")
    else:
        start = 1
        maintimer = QTimer()
        maintimer.timeout.connect(threadworker)
        threadworker()
        maintimer.start(30000)



autorun = checkautorun()
app = QtWidgets.QApplication([])
deltimer = QTimer()
deltimer.timeout.connect(delete_alert)

try:
    window = uic.loadUi("gui.ui")
    ui = window
except:
    window = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(window)

window.setWindowTitle("Commitment Manager")
ui.btn_startstop.clicked.connect(threadbuffer)
ui.list_commitments.setAlternatingRowColors(True)
ui.btn_delete.clicked.connect(deletefromlist)
ui.btn_stop.clicked.connect(stopandclear)
ui.checkbox_autorun.setChecked(autorun)
ui.checkbox_autorun.stateChanged.connect(togglecheck)

addtoList()
if autorun == True:
    threadbuffer()
window.show()
app.exec()