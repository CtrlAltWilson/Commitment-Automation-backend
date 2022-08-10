# -*- coding: utf-8 -*-

from PyQt5 import QtWidgets
from PyQt5.QtCore import QTimer,QThreadPool
from gui import *

from cryptography.fernet import Fernet
import requests
from simple_salesforce import Salesforce
from datetime import datetime


try:
    from src.httpstatus import getRequest
    from src.constrants import newQuery,testQuery,getQuery,getSupportQuery,getFilteredSupportQuery,getFilteredSupportQueryNEWONLY
    from src.caseQuery import caseQuery
    from src.phone import getPhone
    from src.sf_time import isTime, checkTime
    from src.rc import getAgents,createCommit, getCommits,deleteCommit, clearCallbacks, clearAllSkills
    from src.togglecheck import togglecheck, checkautorun, setMinutes
    from src.logs import log
    from src.updatecase import checkSchStatus, resetStatus
    from src.credentials import \
        client_id,              \
        client_secret,          \
        cm_user,                \
        cm_pass,                \
        access_token,           \
        auth_url
except Exception as e:
    print(str(e))
    from httpstatus import getRequest
    from constrants import newQuery, testQuery,getQuery,getSupportQuery,getFilteredSupportQuery,getFilteredSupportQueryNEWONLY
    from caseQuery import caseQuery
    from phone import getPhone
    from sf_time import isTime, checkTime
    from togglecheck import togglecheck, checkautorun, setMinutes
    from rc import getAgents, createCommit, getCommits,deleteCommit, clearCallbacks, clearAllSkills
    from updatecase import checkSchStatus, resetStatus
    from logs import log
    from credentials import     \
        client_id,              \
        client_secret,          \
        cm_user,                \
        cm_pass,                \
        access_token,           \
        auth_url


currentCases = None
maintimer = None
globsf = []
commitscreated = 0
isRunning = 0
stopped = 0
start = 0
sf = None
pulse = 0
blacklist = ["delet","delete","remove","remov"]
f_key = Fernet.generate_key()
fern = Fernet(f_key)
max_commits = 5

def main():
    global globsf,commitscreated, isRunning,pulse
    recent_update = checkTime() 
    if recent_update[1] == 1:
        #clearAllSkills(fern)
        stopandclear()
    if stopped == 1:
        log("stopped")
        return
    commits = getCommits(fern)
    if isRunning == 1 and pulse == 0:
        pass
    elif len(commits) > max_commits and pulse == 0:
        log("Commits limited to {}, there are currently {} in queue.".format(max_commits,len(commits)))
        addtoList()
    else:
        pulse = 0
        isRunning = 1
        if sf == None:
            setSF()
        #desc = sf.Account.describe()
        #field_names=[field['name'] for field in desc['fields']]
        query = getFilteredSupportQuery
        sf_data = caseQuery(sf,query)

        records = sf_data['records']
        if len(records) > 2:
            log("More than 3 new records, changing query")
            query = getFilteredSupportQueryNEWONLY
            sf_data = caseQuery(sf,query)
            records = sf_data['records']

        packaged_case = []
        cases = []
        globsf = []
        bword = None
        if stopped == 1: 
            log("stopped")
            return

        for record in records:

            if stopped == 1: 
                log("stopped")
                return

            isNew = 0
            appendcase = 0
            phone = getPhone(record['SuppliedPhone'], record['ContactPhone'])
            castime = isTime(record['LastModifiedDate'])
            if record['Description'] is not None:
                description = record['Description'].casefold()
            else:
                description == ""
            subject = record['Subject'].casefold()
            if record['Status'] == "New":
                isNew = 1
                if "delete" not in description and "message" not in description:
                    for word in blacklist:
                        if word in description or word in subject:
                            appendcase = 1
                            bword = word
            if phone == 0:
                log("{} has no number!".format(record['CaseNumber']))
            if appendcase == 1:
                log("{} has a blacklisted word: {}".format(record['CaseNumber'],bword))
            if phone != 0 and appendcase == 0:
                cases.append([record['CaseNumber'],record['SuppliedName'],record['Platform__c'],record['LastModifiedDate'],castime,phone,isNew,record])
                globsf.append(record['CaseNumber'])

        if stopped == 1: 
            log("stopped")
            return

        agents = getAgents(fern)
        packaged_case.append(cases)
        packaged_case.append(agents[1])
        packaged_case.append(sf)
        #cases.append(agents)
        #cases.append(sf)
        ui.num_agents.display(agents[1])
        if agents[1] > 1:
            setMinutes()

        if stopped == 1: 
            log("stopped")
            return
        commcount = createCommit(packaged_case,fern)
        try:
            commitscreated += commcount
        except:
            pass
        ui.num_commits.display(commitscreated)
        addtoList()

        if stopped == 1: 
            log("stopped")
            return
    isRunning = 0

def setSF():
    global sf
    try:
        if getRequest(auth_url,client_id,client_secret,cm_user,cm_pass,access_token) != 200:
            log("Error accessing database")
            #return
    except:
        log("Error getRequest")
        return
    session = requests.Session()
    
    if stopped == 1: 
        log("stopped")
        return
    
    try:
        sf = Salesforce(username=cm_user,password=cm_pass,security_token=access_token,client_id=client_id,session=session)
    except Exception as e:
        if "INVALID_LOGIN" in str(e):
            log("Incorrect credentials")

def timeAlert(text):
    log(text)
    ui.label_alert.setText(text)
    ui.label_alert.repaint()
    deltimer.start(3000)

def addtoList():
    log("Updating list")
    commits = getCommits(fern)
    if sf == None:
        setSF()
    resetStatus(sf,commits)
    agents = getAgents(fern)
    #commits.sort()
    ui.list_commitments.clearSelection()
    ui.list_agents.clearSelection()
    ui.list_commitments.clear()
    ui.list_agents.clear()
    if commits != 0 or commits != []:
        for i in range(len(commits)):
            QtWidgets.QListWidgetItem(
                "{}\t{}\t{}".format(commits[i][0].strip(),commits[i][2],commits[i][1]),
                ui.list_commitments
            )
        ui.num_queue.display(ui.list_commitments.count())
    for agent in agents[0]:
        QtWidgets.QListWidgetItem(
            "{}".format(agent),
            ui.list_agents
        )
    ui.num_agents.display(agents[1])
    recent_update = checkTime() 
    ui.label_update_time.setText(recent_update[0])
    clearCallbacks(fern)

def deletefromlist():
    try:
        selected = ui.list_commitments.currentItem().text()
        selected = selected.split("\t")
        deleteCommit(selected[0],fern)
        if sf == None:
            setSF()
        checkSchStatus(sf,selected[0])
        addtoList()
    except:
        log("Nothing to delete!")
        ui.label_delete_alert.setText("Nothing\nto delete!")
        ui.label_delete_alert.repaint()
        deltimer.start(1000)

def delete_alert():
    ui.label_delete_alert.clear()
    ui.label_alert.clear()
    deltimer.stop()

def stopandclear():
    global stopped, start, isRunning
    log("Stopping...")
    ui.label_status.setText("Stopping")
    stopped = 1
    start = 0
    isRunning = 0
    ui.label_delete_alert.clear()
    ui.label_status.setText("Standby")

def threadworker(apulse = 0):
    global stopped,pulse
    if start == 1 and apulse == 0:
        stopped = 0
        QThreadPool.globalInstance().start(main)
    elif apulse == 1:
        pulse = 1
        QThreadPool.globalInstance().start(main)

def pulse():
    ui.label_status.setText("Pulsing")
    threadworker(1)
    ui.label_status.setText("Standby")

def threadbuffer():
    global maintimer, start
    #timeAlert("Starting...")
    ui.label_status.setText("Starting")
    recent_update = checkTime()
    if recent_update[1] == 1:
        timeAlert("It's past time! No more commits will be created!")
        #clearAllSkills(fern)
        ui.label_status.setText("Standby")
    elif start == 1:
        timeAlert("I'm already running!")
    else:
        ui.label_status.setText("Running")
        start = 1
        maintimer = QTimer()
        maintimer.timeout.connect(threadworker)
        threadworker()
        maintimer.start(30000)

autorun = checkautorun()
app = QtWidgets.QApplication([])
deltimer = QTimer()
deltimer.timeout.connect(delete_alert)

window = QtWidgets.QMainWindow()
ui = Ui_MainWindow()
ui.setupUi(window)

window.setWindowTitle("Commitment Manager")

#remove titlebar
#window.setWindowFlags(QtCore.Qt.FramelessWindowHint)

ui.btn_startstop.clicked.connect(threadbuffer)
ui.list_commitments.setAlternatingRowColors(True)

ui.btn_delete.clicked.connect(deletefromlist)
ui.btn_stop.clicked.connect(stopandclear)
ui.btn_pulse.clicked.connect(pulse)
ui.btn_refresh.clicked.connect(addtoList)

ui.checkbox_autorun.setChecked(autorun)
ui.checkbox_autorun.stateChanged.connect(togglecheck)

setMinutes()
addtoList()

if autorun == True:
    threadbuffer()
window.show()
app.exec()