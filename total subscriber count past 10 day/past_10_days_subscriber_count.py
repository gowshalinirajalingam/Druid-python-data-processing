
import pandas as pd
import json
import requests
from datetime import datetime,timedelta

headers = {
   'Content-Type': 'application/json',
}

params = (
   ('pretty', ''),
)

today = (datetime.today()).strftime('%Y-%m-%dT00:00:00.000Z')
last10days = (datetime.today()-timedelta(days=10)).strftime('%Y-%m-%dT00:00:00.000Z')

dfa = pd.DataFrame()
dfb = pd.DataFrame()
dfc = pd.DataFrame()



print("started 1GB processing")
#Less than 1GB#########################################33
with open('past_10_days_<1GB.json', 'r+') as f:
    data1 = json.load(f)
    data1['intervals'] = '{}/{}'.format(last10days,today) # <--- add `interval` value.
    data1["dataSource"]["query"]['intervals'] = '{}/{}'.format(last10days,today)


    f.seek(0)                    #<--- should reset file position to the beginning.
    json.dump(data1, f, indent=4)
    f.truncate()                  # remove remaining part


data1 = open('past_10_days_<1GB.json')     #open interval wriiten json file again
response = requests.post('http://localhost:8080/druid/v2', headers=headers, params=params, data=data1)


res = response.text
ress = res.replace("\n"," ")
loaded_json=json.loads(ress)

for x in loaded_json:    #Loop through jsonArray(In python we call json array as List)
    result = x['event']
    #print (result)
    df1 = pd.DataFrame(result,index = [0])
    #print(df1)
    dfa = dfa.append(df1) 

dfa.rename(columns={'count':'count_<1'}, inplace=True)







print("started 1GB-5GB processing")

#/////////////////////////1GB to 5GB////////////////////////////////
with open('past_10_days_1GBTO5GB.json', 'r+') as f:
    data2 = json.load(f)
    data2['intervals'] = '{}/{}'.format(last10days,today) # <--- add `interval` value.
    data2["dataSource"]["query"]['intervals'] = '{}/{}'.format(last10days,today)


    f.seek(0)                    #<--- should reset file position to the beginning.
    json.dump(data2, f, indent=4)
    f.truncate()                  # remove remaining part


data2 = open('past_10_days_1GBTO5GB.json')     #open interval wriiten json file again
response = requests.post('http://localhost:8080/druid/v2', headers=headers, params=params, data=data2)


res = response.text
ress = res.replace("\n"," ")
loaded_json=json.loads(ress)

for x in loaded_json:    #Loop through jsonArray(In python we call json array as List)
    result = x['event']
    #print (result)
    df2 = pd.DataFrame(result,index = [0])
    #print(df1)
    dfb = dfb.append(df2) 

dfb.rename(columns={'count':'count_1_5'}, inplace=True)




print("started >5GB processing")

#/////////////////////////////////>5GB///////////////////////////////////
with open('past_10_days_>5GB.json', 'r+') as f:
    data3 = json.load(f)
    data3['intervals'] = '{}/{}'.format(last10days,today) # <--- add `interval` value.
    data3["dataSource"]["query"]['intervals'] = '{}/{}'.format(last10days,today)
   

    f.seek(0)                    #<--- should reset file position to the beginning.
    json.dump(data3, f, indent=4)
    f.truncate()                  # remove remaining part


data3 = open('past_10_days_>5GB.json')     #open interval wriiten json file again
response = requests.post('http://localhost:8080/druid/v2', headers=headers, params=params, data=data3)


res = response.text
ress = res.replace("\n"," ")
loaded_json=json.loads(ress)

for x in loaded_json:    #Loop through jsonArray(In python we call json array as List)
    result = x['event']
    #print (result)
    df3 = pd.DataFrame(result,index = [0])
    #print(df1)
    dfc = dfc.append(df3) 

dfc.rename(columns={'count':'count_>5'}, inplace=True)


#Join into one data frame
dff = dfa.join(dfb.set_index('Date'), on='Date')
dffinal = dff.join(dfc.set_index('Date'), on='Date')




import sqlalchemy
import mysql.connector


db_ip="<ip>:<port>"
db_user="<db server user name>"
db_passwd="<db server pw>"
database="db name"

db_conn= sqlalchemy.create_engine('mysql+mysqlconnector://{0}:{1}@{2}/{3}'.format(db_user,db_passwd,db_ip,database),pool_recycle=1,pool_timeout=100000).connect()

dffinal.to_sql(con=db_conn, name='Past_10day_subscriber_count', if_exists='replace',index=False,chunksize=10000)

db_conn.close()
print("sent to db")
