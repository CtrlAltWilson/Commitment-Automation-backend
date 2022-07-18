import requests
import base64

from credentials import rc_auth_key, rc_url,rc_user,rc_pass

def getRequest(fk):
    rc_auth1 = rc_auth_key.encode('utf-8')
    rc_auth2 = base64.b64encode(rc_auth1)
    rc_auth = rc_auth2.decode("utf-8")
    retry = 0
    while retry < 3:
        try:
            print("Getting rc auth")
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
            #print(response.json())
            j = bytes(response.text, 'utf-8')
            k = fk.encrypt(j)
            with open('rc_token.WILSON','wb') as f:
                f.write(k)
            return 1
        except:
            retry += 1