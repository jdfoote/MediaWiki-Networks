import psycopg2
import datetime as dT
import yaml
import sys
sys.path.append("../")
import networkTools as nT
from collections import defaultdict
import datetime


conn = psycopg2.connect("dbname=weRelate user=jeremy")

with open('config.yaml', 'r') as f:
    config = yaml.load(f)

startDate = config['startDate']
endDate = config['endDate']
delta = config['timeDelta']

# Create table
cur = conn.cursor()
cur.execute("SELECT DISTINCT page_category from pages ORDER BY page_category ASC;")
categories = cur.fetchall()
createString = """CREATE TABLE userStats (
startDate date,
endDate date
"""
for category in categories:
    categoryName = category[0] +  '_edits'
    createString += ", {} integer".format(categoryName.replace(' ','_'))
createString += ');'
cur.close()
cur = conn.cursor()
cur.execute(createString)
cur.close()


def addDataToDB(row):
    cur = conn.cursor()
    cur.execute("""INSERT INTO userStats VALUES (%s)""", (row))
    cur.close()


users = nT.getActiveUsers(startDate, endDate)

for user in users:
    print user
    userDict = defaultdict(int)
    userDict['allEdits'] = nT.getEditCount(user, startDate, endDate, False)
    edits = nT.getEdits(user, startDate, endDate)
    currStart = startDate
    currEnd = currStart + datetime.timedelta(days=30)
    currIndex = 0
    # TODO: Need to make sure to attach the last group (if edit_time is not > currEnd)
    while currEnd < endDate and i < len(edits)-1:
        for i, edit in enumerate(edits[currIndex:]):
            if edit[1] < currEnd:
                pageCategory = edit[2]
                userDict[pageCategory] += 1
            else:
                userRow = [currStart, currEnd]
                for c in categories:
                    if c in userDict:
                        userRow.append(userDict[c])
                    else:
                        userRow.append(0)
                if sum(userDict.values()) != len(edits):
                    print "Not equal"
                addDataToDB(userRow)
                # Update stuff for the next iteration
                currIndex += i
                currStart = currEnd
                currEnd += datetime.timedelta(days = 30)
