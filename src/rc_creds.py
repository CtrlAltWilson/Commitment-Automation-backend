import requests
import base64

try:
    from src.credentials import rc_auth_key, rc_url,rc_user,rc_pass
    from src.logs import log
except:
    from credentials import rc_auth_key, rc_url,rc_user,rc_pass
    from logs import log

retry = 0

def getRequest(fk):
    global retry
    if retry == 3:
        return 0
    rc_auth1 = rc_auth_key.encode('utf-8')
    rc_auth2 = base64.b64encode(rc_auth1)
    rc_auth = rc_auth2.decode("utf-8")
    try:
        log("Getting rc auth")
        auth = {'Authorization': 'basic ' + rc_auth}
        response = requests.post(rc_url, headers=auth, \
            json = {
                'grant_type': 'password',
                #'client_id': rc_auth_key,
                #'client_secret': rc_secret,
                'username': rc_user,
                'password': rc_pass,
                'scope' : 'RealTimeApi AdminApi'
            })
        #log(response.json())
        j = bytes(response.text, 'utf-8')
        k = fk.encrypt(j)
        with open('rc_token.WILSON','wb') as f:
            f.write(k)
        return 1
    except Exception as e:
        log(str(e))
        retry += 1
        getRequest(fk)