import json
import requests
from cryptography.fernet import Fernet

try:
    from src.rc_creds import getRequest
    from src.sf_time import getTime,getRCTime
    from src.updatecase import updatecase
    from src.logs import log
    from src.sf_time import checkBlackout
    from src.togglecheck import getMinutes, setMinutes
except:
    from rc_creds import getRequest
    from sf_time import getTime,getRCTime
    from updatecase import updatecase
    from logs import log
    from sf_time import checkBlackout
    from togglecheck import getMinutes, setMinutes

config = None
SSKillID = 	'4271306'

f_key = Fernet.generate_key()
fern = Fernet(f_key)

def main(fk):
    global config
    try:
        with open('rc_token.WILSON','r',encoding='utf-8') as f:
            code = bytes(f.read(), 'utf-8')
            config = fk.decrypt(code).decode()
    except Exception as e:
        log("Main: ",str(e))
        getRequest(fk)
        with open('rc_token.WILSON','r') as f:
            code = bytes(f.read(), 'utf-8')
            config = fk.decrypt(code).decode()
    config = json.loads(config)

def createCommit(arr,fk):
    if len(arr[0]) == 0:
        return
    log("Creating commits({})".format(len(arr[0])))
    retry = 0
    cases = arr[0]
    agents = arr[1]
    sf = arr[2]
    #minutes = 2
    count = 0
    isblackout = checkBlackout()
    while retry < 3:
        try:
            main(fk)
            auth = {'Authorization': 'Bearer ' + config['access_token']}
            url = config['resource_server_base_uri'] + 'services/v13.0/scheduled-callbacks'
            for case in cases:
                k = checkCommits(case[0],case[5],fk)
                #log((case[4] == 1 or case[6] == 1))# and case[5] != 0 and k == 1)
                if (case[4] == 1 or case[6] == 1) and case[5] != 0 and k == 1:
                    minutes = getMinutes()
                    if isblackout == 0:
                        if agents != 0:
                            agents -= 1
                            minutes += 2
                        else:
                            minutes += 12
                        if minutes > 60:
                            minutes = (minutes%5)+1
                    else:
                        if agents != 0:
                            agents -= 1
                            minutes += 2
                        else:
                            minutes += 30
                        if minutes > 120:
                            minutes = (minutes%5)+1
                    setMinutes(minutes)
                    log("Setting commit for ", case[0])
                    updatecase(sf,case[7])
                    newtime = getTime(minutes)
                    log(newtime)
                    res = requests.post(url, headers=auth,json= {
                        'phoneNumber': case[5],
                        'skillId':SSKillID,
                        'scheduleDate': newtime,
                        'firstName':case[0],
                        'lastName':case[1]
                    })
                    r = res.json()
                    log(r)
                    count += 1
                    if count >= 5:
                        return count
            return count
        except Exception as e:
            log("Create Commit: ",str(e))
            getRequest(fk)
            retry += 1
    return 0

def deleteCommit(case,fk):
    log('deleting ',case)
    retry = 0
    while retry < 3:
        try:
            main(fk)
            callbackID = checkDeleteCommit(case,fk)
            auth = {'Authorization': 'Bearer ' + config['access_token']}
            url = config['resource_server_base_uri'] + 'services/v13.0/scheduled-callbacks/{}'.format(callbackID)
            res = requests.delete(url, headers=auth,json={
                'callbackId':callbackID
            })
            r = res.json()
            log(r)
            return 1
        except Exception as e:
            log("DeleteCommit: ",str(e))
            getRequest(fk)
            retry += 1
    return 0

def getCommits(fk):
    log("Getting commits")
    retry = 0
    while retry < 3:
        try:
            main(fk)
            auth = {'Authorization': 'Bearer ' + config['access_token']}
            url = config['resource_server_base_uri'] + 'services/v13.0/skills/{}/scheduled-callbacks'.format(SSKillID)
            res = requests.get(url, headers=auth,json={
                'skillId':SSKillID
            })
            r = res.json()
            #log(r)
            queue = []
            if len(r['callbacks']) > 0:
                for i in r['callbacks']:
                    #print('notes',i['notes'])
                    #log(i['firstName'])
                    queue.append([i['firstName'],i['lastName'],getRCTime(i['callbackTime'])])
            return queue
        except Exception as e:
            log("GetCommits: ",str(e))
            getRequest(fk)
            retry += 1
    return 0

#TODO merge this with getcommit later
def checkCommits(case,phone,fk):
    retry = 0
    while retry < 3:
        try:
            main(fk)
            auth = {'Authorization': 'Bearer ' + config['access_token']}
            url = config['resource_server_base_uri'] + 'services/v13.0/skills/{}/scheduled-callbacks'.format(SSKillID)
            res = requests.get(url, headers=auth,json={
                'skillId':SSKillID
            })
            r = res.json()
            for i in r['callbacks']:
                if i['firstName'] == case:
                    return 0
                if i['dialNumber'] == phone:
                    return 0
            return 1
        except Exception as e:
            log("CheckCommits: ",str(e))
            getRequest(fk)
            retry += 1
    return -1

def checkDeleteCommit(case,fk):
    retry = 0
    while retry < 3:
        try:
            main(fk)
            auth = {'Authorization': 'Bearer ' + config['access_token']}
            url = config['resource_server_base_uri'] + 'services/v13.0/skills/{}/scheduled-callbacks'.format(SSKillID)
            res = requests.get(url, headers=auth,json={
                'skillId':SSKillID
            })
            r = res.json()
            for i in r['callbacks']:
                if i['firstName'] == case:
                    return i['callbackId']
            return 1
        except Exception as e:
            log("CheckDeleteCommit: ",str(e))
            getRequest(fk)
            retry += 1
    return -1

def getAgents(fk):
    retry = 0
    while retry < 3:
        try:
            main(fk)
            log("Getting Agents")
            auth = {'Authorization': 'Bearer ' + config['access_token']}
            url = config['resource_server_base_uri'] + 'services/v13.0/agents/states'
            res = requests.get(url, headers=auth,json={
                'skillId':SSKillID
            })
            r = res.json()
            agents = []
            for agent in r['agentStates']:
                if agent['agentStateName'] == "Available" and agent['teamName'] == "Support":
                    #log(agent)
                    agents.append(agent['firstName'])
            log("Available Agents({}): {}".format(len(agents),agents))
            return [agents,len(agents)]
        except Exception as e:
            log("GetAgents: ",str(e))
            getRequest(fk)
            retry += 1
    return 0

def clearCallbacks(fk,skill = SSKillID):
    try:
        main(fk)
        log("Getting Callbacks {}".format(skill))
        auth = {'Authorization': 'Bearer ' + config['access_token']}
        url = config['resource_server_base_uri'] + 'services/v13.0/contacts/active'
        res = requests.get(url, headers=auth,json={
            'skillId':skill
        })
        r = res.json()
        #print(r)
    
        for callback in r['resultSet']['activeContacts']:
            print("Callbacks: ",callback['contactId'],callback['state'])
            
            if ((callback['skillName'] == 'Support OB')and callback['state'] == 'CallBack') or (skill != SSKillID and callback['state'] != "Active"):
                log("Clearing callback {}".format(callback['contactId']))
                url2 = config['resource_server_base_uri'] + 'services/v13.0/contacts/{}/end'.format(callback['contactId'])
                res2 = requests.post(url2, headers=auth,json={
                    'contactId':callback['contactId']
                })
                res2.json() 
                #print(r2)
        return 1
    except Exception as e:
        #log("ClearCallBacks: ",str(e))
        pass
    return 0

def clearAllSkills(fk):
    try:
        main(fk)
        log("Getting Agents")
        auth = {'Authorization': 'Bearer ' + config['access_token']}
        url = config['resource_server_base_uri'] + 'services/v13.0/skills'
        res = requests.get(url, headers=auth)
        r = res.json()
        for skill in r['skills']:
            #print(skill['skillId'],skill['skillName'])
            clearCallbacks(fk,skill['skillId'])
        return 1
    except Exception as e:
        log("clearAllSkills: ",str(e))
    return 0
#print(clearAllSkills(fern))
#print(clearCallbacks(fern))
#main()