from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QTimer,QThreadPool

from rc import getCommits,deleteCommit, getAgents
from sf_time import checkTime
from guiassist import *
from cryptography.fernet import Fernet

f_key = Fernet.generate_key()
fern = Fernet(f_key)

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
    recent_update = checkTime()
    ui.num_agents.display(agents[1])
    ui.label_update_time.setText(recent_update[0])

def deletefromlist():
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
    deltimer.stop()

def threadworker():
    QThreadPool.globalInstance().start(addtoList)

def threadbuffer():
    global maintimer
    maintimer = QTimer()
    maintimer.timeout.connect(threadworker)
    threadworker()
    maintimer.start(15000)

app = QtWidgets.QApplication([])
deltimer = QTimer()
deltimer.timeout.connect(delete_alert)

try:
    window = uic.loadUi("guiassist.ui")
    ui = window
except:
    window = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(window)

window.setWindowTitle("Commitment Assistant")
ui.list_commitments.setAlternatingRowColors(True)
ui.btn_delete.clicked.connect(deletefromlist)

threadbuffer()

window.show()
app.exec()