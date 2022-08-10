newQuery = """
SELECT 
Id,
AccountId,
CaseNumber,
ContactId,
Description,
OwnerId,
Phone__c,
Status,
Dialer_Status__c,
Sub_Category__c, 
Email

FROM 
Case 

WHERE 
Status = 'New' 
AND 
ContactId != '' 
AND
Subject != 'Operator Call'
"""

testQuery = """
SELECT
FIELDS(ALL)

FROM
Case

WHERE 
CaseNumber = '00664340'

LIMIT
200
"""

getQuery = """
SELECT
Id,
Status,
CaseNumber,
SuppliedName,
PHone__c,
SuppliedPhone,
ContactPhone,
ContactEmail,
LastModifiedDate

FROM
Case

WHERE
Ownerid = '00GU00000018lmTMAQ'
AND
Subject != 'Operator Call'
AND
ContactId != '' 
AND
Net_Promoter_Score_Category__c = 'Support'
AND
PHone__c != '(917) 656-8041'
"""

getSupportQuery = """
SELECT
Id,
Status,
CaseNumber,
SuppliedName,
PHone__c,
SuppliedPhone,
ContactPhone,
ContactEmail,
LastModifiedDate

FROM
Case

WHERE
Ownerid = '00GU00000018lmTMAQ'
AND
(
    Status = 'New' OR 
    Status = 'Scheduled Support Call' OR 
    Status = 'Investigating' OR 
    Status LIKE 'Waiting Call Back%' OR 
    Status = 'Pending Information From Client'
)

ORDER BY
LastModifiedDate

"""

getFilteredSupportQuery = """
SELECT
Id,
Status,
CaseNumber,
ContactId,
SuppliedName,
PHone__c,
SuppliedPhone,
ContactPhone,
ContactEmail,
LastModifiedDate,
Platform__c,
Specific_Issue__c,
Sub_Category__c,
Description,
Subject

FROM
Case

WHERE
Ownerid = '00GU00000018lmTMAQ'
AND
(
    Status = 'New' OR 
    Status = 'Scheduled Support Call' OR 
    Status = 'Waiting Call Back - 2nd Attempt' OR 
    Status = 'Pending Information From Client'
)
AND
(NOT ContactEmail LIKE '%@raptortech.com')
AND
(NOT ContactEmail LIKE '%@lobbyguard.com')
AND
(NOT ContactEmail LIKE '%@vsoft.uservoice.com')
AND
(NOT Subject LIKE '%Installation Request%')
AND
ContactId != ''

ORDER BY
LastModifiedDate

"""
#    Status LIKE 'Waiting Call Back%' OR 

getFilteredSupportQueryNEWONLY = """
SELECT
Id,
Status,
CaseNumber,
ContactId,
SuppliedName,
PHone__c,
SuppliedPhone,
ContactPhone,
ContactEmail,
LastModifiedDate,
Platform__c,
Specific_Issue__c,
Sub_Category__c,
Description,
Subject

FROM
Case

WHERE
Ownerid = '00GU00000018lmTMAQ'
AND
Status = 'New'
AND
(NOT ContactEmail LIKE '%@raptortech.com')
AND
(NOT ContactEmail LIKE '%@lobbyguard.com')
AND
(NOT ContactEmail LIKE '%@vsoft.uservoice.com')
AND
(NOT Subject LIKE '%Installation Request%')
AND
ContactId != ''

ORDER BY
LastModifiedDate

"""