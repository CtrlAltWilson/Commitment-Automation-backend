import json
import requests

try:
    from src.rc_creds import getRequest
    from src.sf_time import getTime,getRCTime
    from src.updatecase import updatecase
    from src.logs import log
except:
    from rc_creds import getRequest
    from sf_time import getTime,getRCTime
    from updatecase import updatecase
    from logs import log

config = None
SSKillID = 	'4271306'

def main(fk):
    global config
    log(fk)
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
    log("creating commits")
    retry = 0
    cases = arr[0]
    agents = arr[1]
    sf = arr[2]
    minutes = 2
    count = 0
    while retry < 3:
        try:
            main(fk)
            auth = {'Authorization': 'Bearer ' + config['access_token']}
            url = config['resource_server_base_uri'] + 'services/v13.0/scheduled-callbacks'
            for case in cases:
                k = checkCommits(case[0],case[5],fk)
                #log((case[4] == 1 or case[6] == 1))# and case[5] != 0 and k == 1)
                if (case[4] == 1 or case[6] == 1) and case[5] != 0 and k == 1:
                    if agents != 0:
                        agents -= 1
                        minutes += 2
                    else:
                        minutes += 12
                    if minutes > 65:
                        minutes = (minutes%5)+1
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
            for i in r['callbacks']:
                #log(i['firstName'])
                queue.append([i['firstName'],i['lastName'],getRCTime(i['callbackTime'])])
            return queue
        except Exception as e:
            log("GetCommits: ",str(e))
            getRequest(fk)
            retry += 1
    return 0
#log(getCommits())

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

#main()