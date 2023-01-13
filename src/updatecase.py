try:
    from src.logs import log
    from src.caseQuery import caseQuery
    from src.sf_time import isTime
except: 
    from logs import log
    from caseQuery import caseQuery
    from sf_time import isTime

import threading

def updatecase(sf,record):
    try:
        id = record['Id']
        description = record['Description'].casefold()
        status = record['Status']
        platform = record['Platform__c']
        
        cate = 'Visitor Management'
        subcate = 'Training_VM'
        specate = 'Visitor Module'

        sf.Case.update(id,{'Department__c':'Support (Technical)'})

        if status == "New":
            sf.Case.update(id,{'Status':'Scheduled Support Call'})
        #log(record)
        #log("category c is ",record['Sub_Category__c'])
        if record['Sub_Category__c'] is None:    
            if "barcode" in description:
                cate = 'Kiosk'
                subcate = 'Self-Service Kiosk'
                specate = 'Scanner Configuration'
            elif "scan" in description:
                subcate = 'CR5400'
                specate = 'Device Manager Unrecognized'
            elif "print" in description:
                subcate = 'DYMO 450 Turbo'
                specate = 'Device Manager Unrecognized'

            sf.Case.update(id,{'Category__c':cate})
            sf.Case.update(id,{'Sub_Category__c':subcate})
            sf.Case.update(id,{'Specific_Issue__c':specate})

        if platform == None or platform == "":            
            if "lobbyguard" in description or "lobby guard" in description:
                sf.Case.update(id,{'Platform__c':'LobbyGuard'})
            else:
                sf.Case.update(id,{'Platform__c':'Raptor 6'})
    except Exception as e:
        log(str(e))

def checkSchStatus(sf,case):
    query = "SELECT Id, Status FROM Case WHERE CaseNumber = '{}'".format(case)
    sf_data = caseQuery(sf,query)
    record = sf_data['records'][0]
    id = record['Id']
    if record['Status'] == "Scheduled Support Call":
        log("Setting {} to new".format(case))
        sf.Case.update(id,{'Status':'New'})
    

def resetStatus(sf,commits):
    query = "SELECT Id, Status, CaseNumber FROM Case WHERE Status = 'Scheduled Support Call' AND Ownerid = '00GU00000018lmTMAQ'"
    sf_data = caseQuery(sf, query)
    records = sf_data['records']
    commit_list = []
    try:
        for i in range(len(commits)):
            commit_list.append(commits[i][0].strip())
        #print("commitlist ",commit_list)
        for record in records:
            if record['CaseNumber'] not in commit_list:
                log("Case {} not in commit queue, setting back to new".format(record['CaseNumber']))
                sf.Case.update(record['Id'],{'Status':'New'})
    except:
        pass
    
    newStatus(sf,commit_list)

def newStatus(sf,commits):
    try:
        query = "SELECT Id, Status, CaseNumber FROM Case WHERE Status = 'New' AND Ownerid = '00GU00000018lmTMAQ'"
        sf_data = caseQuery(sf, query)
        records = sf_data['records']
        for record in records:
            if record['CaseNumber'] in commits:
                log("Case {} in commit queue but not updated, updating to Scheduled".format(record['CaseNumber']))
                sf.Case.update(record['Id'],{'Status':'Scheduled Support Call'})
    except:
        pass

def second_attempt(sf):
    def secondattemptemail(record):
        log("Sending Second Attempt Email for case {}".format(record['CaseNumber']))
        ID = record['Id']
        sf.Case.update(ID,{'Waiting_Call_Back_1st_Attempt_Email_Sent__c':True})
        sf.Case.update(ID,{'Status':'Waiting Call Back - 2nd Attempt'})

    query = "SELECT Id, LastModifiedDate, CaseNumber FROM Case WHERE Status = 'Waiting Call Back - 1st Attempt' AND Ownerid = '00GU00000018lmTMAQ'"
    sf_data = caseQuery(sf, query)
    records = sf_data['records']
    for record in records:
        checkTime = isTime(record['LastModifiedDate'], ho = 3)
        if checkTime == 1:
            k1 = threading.Thread(target=secondattemptemail,args=[record])
            k1.start()

def third_attempt(sf):
    def thirdattempemail(record):
        log("Sending Third Attempt Email for case {}".format(record['CaseNumber']))
        ID = record['Id']
        if record['Platform__c'] is None:
            sf.Case.update(ID,{'Platform__c':'Raptor 6'})
        contact_id = record['ContactId']
        contact = sf.Contact.get(contact_id)
        temp_email = contact['Email']
        sf.Contact.update(contact_id,{'Email':''})
        sf.Case.update(ID,{'Status':'Closed - Client Unresponsive'})
        sf.Contact.update(contact_id,{'Email':temp_email})

    query = "SELECT Id, LastModifiedDate, CaseNumber, ContactId,Platform__c FROM Case WHERE Status = 'Waiting Call Back - 2nd Attempt' AND Ownerid = '00GU00000018lmTMAQ'"
    sf_data = caseQuery(sf, query)
    records = sf_data['records']
    for record in records:
        checkTime = isTime(record['LastModifiedDate'], ho = 3)
        if checkTime == 1:
            k1 = threading.Thread(target=thirdattempemail,args=[record])
            k1.start()
