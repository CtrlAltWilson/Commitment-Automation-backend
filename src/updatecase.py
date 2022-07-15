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
        if record['Sub_Category__c'] == "":    
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
        print(str(e))