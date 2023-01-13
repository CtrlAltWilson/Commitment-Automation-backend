# -*- coding: utf-8 -*-

from PyQt5 import QtWidgets
from PyQt5.QtCore import QTimer,QThreadPool

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
    from src.updatecase import checkSchStatus, resetStatus,second_attempt, third_attempt
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
    from updatecase import checkSchStatus, resetStatus,second_attempt, third_attempt
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
sf = None

f_key = Fernet.generate_key()
fern = Fernet(f_key)
gui_version = 2
blacklist = ["delet","delete","remove","remov"]
send_attempts = 0 #0 None, 1 second attempts, 2 third attempts, 3 both 1 and 2, 4 roll over to email_attempts
email_attempts_num = 0
commitscreated = 0
max_commits = 4
isRunning = 0
startup = 1
stopped = 0
globsf = []
start = 0
pulse = 0

if gui_version == 1:
    from gui import *
elif gui_version == 2:
    from gui_control import *

def main():
    global globsf,commitscreated, isRunning,pulse
    log("Starting Main")
    if stopped == 1:
        log("stopped")
        return
    
    recent_update = checkTime() 
    commits = getCommits(fern)

    if sf == None:
        setSF()

    if isRunning == 1 and pulse == 0:
        pass
    elif len(commits) > max_commits and pulse == 0:
        log("Commits limited to {}, there are currently {} in queue.".format(max_commits,len(commits)))
    elif recent_update[1] == 1 and pulse == 0:
        ui.label_status.setText("Idle")
    elif len(commits) < max_commits:
        pulse = 0
        isRunning = 1

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

        if stopped == 1: 
            log("stopped")
            return
    #second_attempt(sf)
    addtoList()
    if stopped == 1: 
        log("stopped")
        return
    isRunning = 0

def setSF():
    global sf
    x = '00673979'
    query = """SELECT Id FROM Case WHERE CaseNumber = '{}' """.format(x)
    try:
        caseQuery(sf,query)
    except:
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

def timeAlert(text, timerset = 3000):
    log(text)
    ui.label_alert.setText(text)
    ui.label_alert.repaint()
    deltimer.start(timerset)

def addtoList():
    global startup
    log("Updating list")
    commits = getCommits(fern)
    if sf == None:
        setSF()
    if startup != 1 and gui_version == 1:
        try:
            resetStatus(sf,commits)
        except:
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
    if gui_version == 1:
        email_attempts(sf)
        if startup != 1:
            clearCallbacks(fern)
    startup = 0
    log("Updating List Completed")

def email_attempts(sf2 = None):
    log("Starting Email Attempts")
    setSF()
    if sf2 == None:
        sf2 = sf
    if send_attempts == 4:
        sa = email_attempts_num
    else:
        sa = send_attempts
    ui.label_status.setText("Sending Emails...")
    if sa == 1:
        second_attempt(sf2)
    elif sa == 2:
        third_attempt(sf2)
    elif sa == 3:
        third_attempt(sf2)
        second_attempt(sf2)
    ui.label_status.setText("Emails Sent!")
    log("Email Attempts Completed")


def deletefromlist():
    if startup == 1:
        return
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
    if startup == 1:
        return
    log("Stopping...")
    ui.label_status.setText("Stopping")
    stopped = 1
    start = 0
    isRunning = 0
    ui.label_delete_alert.clear()
    ui.label_status.setText("Standby")

def threadworker(apulse = 0):
    global stopped,pulse,email_attempts_num
    setSF()
    if start == 1 and apulse == 0: #run
        if startup == 1:
            return
        stopped = 0
        QThreadPool.globalInstance().start(main)
    elif apulse == 1: #pulse
        pulse = 1
        QThreadPool.globalInstance().start(main)
    elif apulse == 2: #startup and refresh
        ui.label_status.setText("Setting up")
        QThreadPool.globalInstance().start(startup_check)
        QThreadPool.globalInstance().start(addtoList)
    elif apulse == 3: #first attempts
        email_attempts_num = 1
        QThreadPool.globalInstance().start(email_attempts)
    elif apulse == 4: #second attempts
        email_attempts_num = 2
        QThreadPool.globalInstance().start(email_attempts)
    elif apulse == 5: #reset case status
        QThreadPool.globalInstance().start(RS)
    elif apulse == 6: #clear case callbacks
        QThreadPool.globalInstance().start(CC)
    elif apulse == 7: #clear all callbacks
        QThreadPool.globalInstance().start(CAS)

def RS(): #reset status
    commits = getCommits(fern)
    resetStatus(sf,commits)

def CC(): #clear callbacks
    clearCallbacks(fern)

def CAS(): #clear all callbacks
    clearAllSkills(fern)


def startup_check():
    while(startup == 1):
        pass
    ui.label_status.setText("Ready")


def pulse():
    if startup == 1:
        return
    ui.label_status.setText("Pulsing")
    threadworker(1)
    ui.label_status.setText("Standby")

def refresh():
    if startup == 1:
        return
    threadworker(2)

def attempts_1():
    if startup == 1:
        return
    threadworker(3)

def attempts_2():
    if startup == 1:
        return
    threadworker(4)

def reset_case_status():
    if startup == 1:
        return
    threadworker(5)

def clear_case_callbacks():
    if startup == 1:
        return
    threadworker(6)

def clear_all_callbacks():
    if startup == 1:
        return
    threadworker(7)


def threadbuffer():
    global maintimer, start
    #timeAlert("Starting...")
    ui.label_status.setText("Starting")
    recent_update = checkTime()
    if recent_update[1] == 1:
        timeAlert("It's past time! No more commits will be created!")
        #clearAllSkills(fern)
        #ui.label_status.setText("Standby")
    if start == 1:
        timeAlert("I'm already running!")
    else:
        if recent_update[1] == 1:
            timeAlert("It's past time! No more commits will be created!")
            ui.label_status.setText("Idle")
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
log("Starting UI")
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
ui.btn_refresh.clicked.connect(refresh)

ui.checkbox_autorun.setChecked(autorun)
ui.checkbox_autorun.stateChanged.connect(togglecheck)

setMinutes()
log(('Using GUI Version {}').format(gui_version))
if gui_version == 1:
    threadworker(2)
elif gui_version == 2:
    startup = 0
    send_attempts = 4
    ui.btn_attempts_1.clicked.connect(attempts_1)
    ui.btn_attempts_2.clicked.connect(attempts_2)
    ui.btn_case_status.clicked.connect(reset_case_status)
    ui.btn_callbacks.clicked.connect(clear_case_callbacks)
    ui.btn_all_callbacks.clicked.connect(clear_all_callbacks)
#addtoList()
if autorun == True:
    threadbuffer()
log("UI Complete")
window.show()
app.exec()