import requests

def getRequest(url,cid,cs,u,p,token):
#    response = requests.post(url, data = {
#        'client_id': cid,
#        'client_secret': cs,
#        'grant_type':'password',
#        'username': u,
#        'password': p
#    })

    #json_res = response.json()
    try:
        auth = {'Authorization': 'Bearer ' + token}

        #instance_url = json_res['instance_url']

        #url = instance_url + '/services/data/v45.0/sobjects/contact/describe'
        res = requests.get(url, headers=auth)
        r = res.status_code
        return r
    except:
        return 0