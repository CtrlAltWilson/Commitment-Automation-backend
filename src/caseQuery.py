import pandas as pd

def caseQuery(sf,query,createcsv = 0):
    sf_data = sf.query_all(query)
    try:
        sf_df = pd.DataFrame(sf_data['records']).drop(columns='attributes')
    except:
        sf_df = pd.DataFrame(sf_data['records'])

    #print(sf_df)
    
    if createcsv == 1:
        sf_df.to_csv("table.csv")
    
    return sf_data
