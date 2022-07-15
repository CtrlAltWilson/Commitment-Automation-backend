import re

def getPhone(phone1, phone2):
    phone1 = clean(phone1)
    phone2 = clean(phone2)
    if checkPhone(phone1) == 1:
        return phone1
    else:
        if checkPhone(phone2) == 1:
            return phone2
    return 0            

def clean(phone):
    phone = str(phone)
    phone = re.sub('[\(\)\-\.\ ]','',phone)
    phone = re.sub(r"([A-Z]+)",'',phone)
    phone = re.sub(r"([a-z]+)",'',phone)
    return phone[0:10]

def checkPhone(phone):
    if (phone is None) or (phone == "") or ('+' in phone) or (len(phone) < 10):
        return 0
    return 1