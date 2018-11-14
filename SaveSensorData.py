# This code reads from the Thingful node, gets  list of all Sensors
# The code then reads through the list of sensors and counts the number with a location of
# zero (at the moment assumes if x=0 y=0)
# Then displays percentage that are zero locations
# Documentation for GROW node
# https://growobservatory.github.io/ThingfulNode/#tag/Locations
#
#
#

import requests, json, sys
import time
# secret contains API Key.  Not in Github repo !
# expects  AuthCode='API Key obtained from Thingful'
# see
# https://growobservatory.github.io/ThingfulNode/#
# how to get a Key
from Secret import AuthCode

import mysql.connector
from mysql.connector import errorcode
conn = mysql.connector.connect(user='root', password='dacjd156n.',
                              host='mysql',)
#conn.set_character_set('UTF8MB4')

cursor = conn.cursor()
cursor.execute('SET NAMES UTF8MB4;')
cursor.execute('SET CHARACTER SET UTF8MB4;')
cursor.execute('SET character_set_connection=UTF8MB4;')


DB_NAME = 'Sensors'

TABLES = {}
TABLES['sensordata'] = (
    "CREATE TABLE if not exists Sensors.sensordata ("
    "  ID int(11) NOT NULL AUTO_INCREMENT,"
    "  SerialNumber  varchar(60) NOT NULL,"
    "  latitude float NOT NULL,"
    "  longitude float NOT NULL,"
    "  FirstSampleTimestamp  datetime NOT NULL,"
    "  LastFetchedSampleTimestamp date NOT NULL,"
    "  FirstSampleDate datetime NOT NULL,"
    "  LastFetchedSampleDate date NOT NULL,"
    "  Name varchar(200) NOT NULL,"
    "  PRIMARY KEY (ID)"
    ") ENGINE=InnoDB")

def create_database(cnx,cursor):
    print "Trying database creation"
    try:
        cursor.execute(
            "CREATE DATABASE IF NOT EXISTS {} DEFAULT CHARACTER SET = 'utf8' ".format(DB_NAME))
    except mysql.connector.Error as err:
        print("Failed creating database: {}".format(err))
        exit(1)
    print "database created"
    try:
		cnx.database = DB_NAME
    except mysql.connector.Error as err:
		if err.errno == errorcode.ER_BAD_DB_ERROR:
			create_database(cursor)
			cnx.database = DB_NAME
		else:
			print(err)
			exit(1)
    print  "creating tables"
    for name, ddl in TABLES.iteritems():
		try:
			print("Creating table {}: ".format(name))
			cursor.execute(ddl)
		except mysql.connector.Error as err:
			if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
				print("already exists.")
			else:
				print(err.msg)
		else:
			print("OK")



def insert_sensor(cnx,cursor,SerialNumber,latitude,longitude,FirstSampleTimestamp,LastFetchedSampleTimestamp,FirstSampleDate,LastFetchedSampleDate,Name):
	add_user = ("INSERT INTO Sensors.sensordata "
               "(SerialNumber,latitude,longitude,FirstSampleTimestamp,LastFetchedSampleTimestamp,FirstSampleDate,LastFetchedSampleDate,Name) "
               "VALUES (%s,%s,%s,%s,%s,%s,%s,%s)")
	print (add_user)
	cursor.execute(add_user,(SerialNumber,latitude,longitude,FirstSampleTimestamp,LastFetchedSampleTimestamp,FirstSampleDate,LastFetchedSampleDate,Name))
	cnx.commit()

def trunc_table(cnx,cursor):
   truncate = ("truncate Sensors.sensordata ")
   print (truncate)
   cursor.execute(truncate)
   cnx.commit()

create_database(conn,cursor)
trunc_table(conn,cursor)
url = "https://grow.thingful.net/api/entity/locations/get"
headers = {"Authorization": "Bearer {0}".format(AuthCode)}
payload = json.dumps({'DataSourceCodes': ['Thingful.Connectors.GROWSensors'] })

response = requests.post(url, headers=headers, data=payload)

jResp = response.json()

# exit if status code is not ok
if response.status_code != 200:
  print("Unexpected response: {0}. Status: {1}. Message: {2}".format(response.reason, response.status, jResp['Exception']['Message']))
  sys.exit()

#print json.dumps(jResp,indent=4,sort_keys=True)
#for key in jResp.items():
#    print key
#    print
#print jResp["Locations"]

Locations = jResp["Locations"]
numSensor=len(Locations)
# print("Number of Sensors : {0}".format(numSensor))

xCount=0
yCount=0
Count=0
for thing in Locations:
  # print thing
  th=Locations[thing]
  x=th["X"]
  y=th["Y"]

  # print json.dumps(th,indent=4,sort_keys=True)
  # print x,y
  if (x==0):
      xCount+=1
  if (y==0):
      yCount+=1
  if ((x==0) and (y==0)):
      Count+=1
  fx=float(x)
  fy=float(y)
  FirstSampleTimestamp=th["FirstSampleTimestamp"]
  FirstSampleDate=FirstSampleTimestamp[:8]
  LastFetchedSampleTimestamp=th["LastFetchedSampleTimestamp"]
  LastFetchedSampleDate=LastFetchedSampleTimestamp[:8]
  Name=th["Name"]
  SerialNumber=th["SerialNumber"]
  print("{0},{1},{2},{3},{4},{5},{6},{7}".format(SerialNumber,round(x,2),round(y,2),FirstSampleTimestamp,LastFetchedSampleTimestamp,FirstSampleDate,LastFetchedSampleDate,Name.encode('utf-8')))
  insert_sensor(conn,cursor,SerialNumber,round(x,2),round(y,2),FirstSampleTimestamp,LastFetchedSampleTimestamp,FirstSampleDate,LastFetchedSampleDate,Name.encode('utf-8'))
#  print(Name)

Percent= float(xCount)/float(numSensor)*100
cursor.close()
conn.close()

# print("Blanks Total {0} | x-coord {1} | y-coord {2} | Percentage Blank {3}".format(Count, xCount, yCount, Percent))
