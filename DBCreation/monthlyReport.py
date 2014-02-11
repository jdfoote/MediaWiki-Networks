import psycopg2
import datetime as dT
import yaml
import sys
sys.path.append("../")
import networkTools as nT
import csv

resultsFile = './results.csv'
conn = psycopg2.connect("dbname=testdata user=kedra")

with open('../config.yaml', 'r') as f:
    config = yaml.load(f)

startDate = config['startDate']
endDate = config['endDate']
delta = dT.timedelta(days=config['timeDelta'])

currDate = startDate
dateList = []
while currDate < endDate:
    dateList.append(currDate)
    currDate += delta

## Create table
#cur = conn.cursor()
#cur.execute("SELECT DISTINCT page_category from pages ORDER BY page_category ASC;")
#categories = [x[0] for x in cur.fetchall()]
## Create sql-friendly descriptions
#SQLCategories = [c.replace(' ','_') + '_edits' for c in categories]
#createString = """CREATE TABLE userStats (
#user_id integer,
#start_date date,
#end_date date,
#all_edits integer
#"""
#for category in SQLCategories:
#    createString += ", {} integer".format(category)
#createString += ', active_days integer);'
#cur.close()
#cur = conn.cursor()
#cur.execute(createString)
#conn.commit()


def addDataToDB(dataFile):
    cur = conn.cursor()
    cur.copy_from(dataFile, 'userstats')
    cur.close()

print startDate, endDate, dateList
users = nT.getActiveUsers(startDate, endDate)

print "starting inserting"
with open(resultsFile, 'wb') as f:
    o = csv.writer(f, delimiter = '\t')
    for user in users:
        print "{} starting"
        for currStart in dateList:
            currEnd = currStart + delta
            edits = nT.getEdits(user, currStart, currEnd)
            # Intialize list of active days
            activeDays = []
            # Initialize dictionary
            userDict = {c:0 for c in categories}
            allEdits = nT.getEditCount(user, currStart, currEnd, False)
            # If we're past our date, then stop.
            for edit in edits:
                pageCategory = edit[2]
                userDict[pageCategory] += 1
                activeDays.append(edit[1].date())
            userRow = [user, currStart, currEnd, allEdits]
            for c in categories:
                userRow.append(userDict[c])
            if sum([userDict[c] for c in categories]) != len(edits):
                print userDict
                print currStart
                print i
                print edits
                raise Exception("Sum of edit counts doesn't match number of edits")
            # Add entry for number of active days
            days = len(set(activeDays))
            if days > 30:
                print activeDays
                print user
                raise Exception("Too many days!")
            userRow.append(days)
            o.writerow(userRow)
            # Update stuff for the next iteration
with open(resultsFile, 'rb') as f:
    addDataToDB(f)
