#curl -X 'POST' -H 'Content-Type:application/json' -d @quickstart/tutorial/wikipedia-top-pages.json http://localhost:8082/druid/v2?pretty

import pandas as pd
import json
import pandasql as ps
import requests
from datetime import datetime,timedelta

headers = {
   'Content-Type': 'application/json',
}

params = (
   ('pretty', ''),
)

todayplus1 = (datetime.today()+timedelta(days=1)).strftime('%Y-%m-%dT%H:00:00.000Z')
last2month = (datetime.today()-timedelta(days=63)).strftime('%Y-%m-%dT%H:00:00.000Z')


with open('query.json', 'r+') as f:
    data = json.load(f)
    data['intervals'] = '{}/{}'.format(last2month,todayplus1) # <--- add `interval` value.
    f.seek(0)                    #<--- should reset file position to the beginning.
    json.dump(data, f, indent=4)
    f.truncate()                  # remove remaining part

data = open('query.json')     #open interval wriiten json file again
response = requests.post('http://localhost:8080/druid/v2', headers=headers, params=params, data=data)


res = response.text
ress = res.replace("\n"," ")
loaded_json=json.loads(ress)

df = pd.DataFrame()
for x in loaded_json:    #Loop through jsonArray(In python we call json array as List)
    result = x['event']
    #print (result)
    df1 = pd.DataFrame(result,index = [0])
    #print(df1)
    df = df.append(df1) 
    
df['timestamp'] = df['timestamp'].astype('datetime64')
    
df.dtypes
df['weekofyear'] = df['timestamp'].dt.week

#monday=0  to sunday=6
df['dayofweek'] = df['timestamp'].dt.dayofweek

df['weekname'] =df['timestamp'].dt.strftime('%A')

df['year'] =df['timestamp'].dt.strftime('%Y')

df['month'] =df['timestamp'].dt.strftime('%m')

df['monthname'] =df['timestamp'].dt.strftime('%b')

df['date'] = df['timestamp'].dt.strftime('%d')

df['Hour'] = df['timestamp'].dt.strftime('%H')

df=df.sort_values('timestamp')

#df.to_csv("DPI_hourly_summary.csv")

#mysql connection
# python3 -m pip install mysql-connector
import sqlalchemy
import mysql.connector

db_ip=""
db_user=""
db_passwd=""
database=""

db_conn= sqlalchemy.create_engine('mysql+mysqlconnector://{0}:{1}@{2}/{3}'.format(db_user,db_passwd,db_ip,database),pool_recycle=1,pool_timeout=100000).connect()

df.to_sql(con=db_conn, name='DPI_hourly_summary', if_exists='replace',index=False,chunksize=10000)

db_conn.close()



#///////////////////
#Month
todayy = (datetime.today()).strftime('%Y-%m-%d')
thismonthday1 = (datetime.today()).strftime('%Y-%m-01')
lastmonth= (datetime.today()-timedelta(days=30)).strftime('%Y-%m-%d')
lastmonthday1 = (datetime.today()-timedelta(days=30)).strftime('%Y-%m-01')



q1= """
SELECT a.district,b.DRR,(b.DRR - a.CurrentMonthTotalUsage) as Variance
FROM (SELECT district,sum(usage_Bytes)/(1024*1024*1024) as CurrentMonthTotalUsage 
from df 
WHERE timestamp BETWEEN '{}' and '{}'
GROUP BY district) a

INNER JOIN

(SELECT district,sum(usage_Bytes)/(1024*1024*1024) as DRR 
from df 
WHERE timestamp BETWEEN '{}' and '{}'
GROUP BY district) b
on a.district = b.district
""".format(thismonthday1,todayy,lastmonthday1,lastmonth)     #Passing pandas variable into pandasql
monthlydf = ps.sqldf(q1, locals())

monthlydf.to_csv("DRR_Variance_table.csv")


#Hour
todayweek = datetime.today().strftime('%Y-%m-%d %H:00')
todayweekmid = datetime.today().strftime('%Y-%m-%d 00:00')

lastweek = (datetime.today()-timedelta(days=7)).strftime('%Y-%m-%d %H:00')
lastweekmid = (datetime.today()-timedelta(days=7)).strftime('%Y-%m-%d 00:00')

q2= """
SELECT sum(usage_Bytes)/(1024*1024*1024) as ThisWeekUsageTotal
FROM df
WHERE timestamp BETWEEN '{}' and '{}'

""".format(todayweekmid,todayweek)     #Passing pandas variable into pandasql
thisweekTotal = ps.sqldf(q2, locals())

q3= """
SELECT sum(usage_Bytes)/(1024*1024*1024) as lastWeekUsageTotal
FROM df
WHERE timestamp BETWEEN '{}' and '{}'

""".format(lastweekmid,lastweek)     #Passing pandas variable into pandasql
lastweekTotal = ps.sqldf(q3, locals())

frames = [thisweekTotal,lastweekTotal]
resultdf=pd.concat(frames)    #


q4= """
select count(*)
from df

""".format(lastmonth,todayy)     #Passing pandas variable into pandasql
ll = ps.sqldf(q4, locals())


