import json
import requests

from rc_creds import getRequest
from sf_time import getTime,getRCTime

config = None
SSKillID = 	'4271306'

#keep
def main(fk):
    global config
    print(fk)
    try:
        with open('rc_token.WILSON','r',encoding='utf-8') as f:
            code = bytes(f.read(), 'utf-8')
            config = fk.decrypt(code).decode()
    except Exception as e:
        print(str(e))
        getRequest(fk)
        with open('rc_token.WILSON','r') as f:
            code = bytes(f.read(), 'utf-8')
            config = fk.decrypt(code).decode()
    config = json.loads(config)


def deleteCommit(case,fk):
    print('deleting ',case)
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
            print(r)
            return 1
        except Exception as e:
            print(str(e))
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
            #print(r)
            queue = []
            for i in r['callbacks']:
                #print(i['firstName'])
                queue.append([i['firstName'],i['lastName'],getRCTime(i['callbackTime'])])
            return queue
        except Exception as e:
            print(str(e))
            getRequest(fk)
            retry += 1
    return 0


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
            print(str(e))
            getRequest(fk)
            retry += 1
    return -1

def getAgents(fk):
    retry = 0
    while retry < 3:
        try:
            main(fk)
            print("Getting Agents")
            auth = {'Authorization': 'Bearer ' + config['access_token']}
            url = config['resource_server_base_uri'] + 'services/v13.0/agents/states'
            res = requests.get(url, headers=auth,json={
                'skillId':SSKillID
            })
            r = res.json()
            agents = []
            roi = []
            for agent in r['agentStates']:
                if agent['agentStateName'] == "Available":
                    if agent['teamName'] == "Support":
                        agents.append(agent['firstName'])
                    elif "roi" in agent['teamName'].casefold():
                        roi.append(agent['firstName'])
            print("Available Agents({}): {}".format(len(agents),agents))
            return [agents,len(agents),roi]
        except Exception as e:
            print(str(e))
            getRequest(fk)
            retry += 1
    return 0

#main()