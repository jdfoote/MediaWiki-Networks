import psycopg2
import datetime as dT
import yaml
import sys
sys.path.append("../")
import networkTools as nT
import csv

resultsFile = './results.csv'
conn = psycopg2.connect("dbname=weRelate user=jeremy")

with open('config.yaml', 'r') as f:
    config = yaml.load(f)

startDate = config['startDate']
endDate = config['endDate']
delta = config['timeDelta']

# Create table
cur = conn.cursor()
cur.execute("SELECT DISTINCT page_category from pages ORDER BY page_category ASC;")
categories = [x[0] for x in cur.fetchall()]
# Create sql-friendly descriptions
SQLCategories = [c.replace(' ','_') + '_edits' for c in categories]
createString = """CREATE TABLE userStats (
user_id integer,
start_date date,
end_date date,
all_edits integer
"""
for category in SQLCategories:
    createString += ", {} integer".format(category)
createString += ', active_days integer);'
cur.close()
cur = conn.cursor()
cur.execute(createString)
conn.commit()


def addDataToDB(dataFile):
    cur = conn.cursor()
    cur.copy_from(dataFile, 'userstats')
    cur.close()

users = nT.getActiveUsers(startDate, endDate)

print "starting inserting"
with open(resultsFile, 'wb') as f:
    o = csv.writer(f, delimiter = '\t')
    for user in users:
        print user
        edits = nT.getEdits(user, startDate, endDate)
        currStart = startDate
        currEnd = currStart + dT.timedelta(days=30)
        currIndex = 0
        while currIndex < len(edits):
            # Intialize list of active days
            activeDays = []
            # Initialize dictionary
            userDict = {c:0 for c in categories}
            allEdits = nT.getEditCount(user, currStart, currEnd, False)
            # If we're past our date, then stop.
            if currStart > endDate:
                break
            # Go through each remaining edit, adding them to dictionary
            for i, edit in enumerate(edits[currIndex:]):
                if edit[1].date() <= currEnd:
                    pageCategory = edit[2]
                    userDict[pageCategory] += 1
                    activeDays.append(edit[1].date())
                # If it's after the current end, then don't record it.
                else:
                    # Correct i so that we don't miss the last edit
                    i -= 1
                    break
            userRow = [user, currStart, currEnd, allEdits]
            for c in categories:
                userRow.append(userDict[c])
                if sum([userDict[c] for c in categories]) != i+1:
                    print userDict
                    print currStart
                    print i
                    print edits
            # Add entry for number of active days
            userRow.append(len(set(activeDays)))
            o.writerow(userRow)
            # Update stuff for the next iteration
            currIndex += i + 1
            currStart = currEnd
            currEnd += dT.timedelta(days = 30)
with open(resultsFile, 'rb') as f:
    addDataToDB(f)
