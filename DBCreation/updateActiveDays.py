import psycopg2
import datetime as dT
import yaml
import sys
sys.path.append("../")
import networkTools as nT
import csv

resultsFile = './activeDays.csv'
conn = psycopg2.connect("dbname=weRelate user=jeremy")

with open('config.yaml', 'r') as f:
    config = yaml.load(f)

startDate = config['startDate']
endDate = config['endDate']
delta = config['timeDelta']


users = nT.getActiveUsers(startDate, endDate)

print "starting inserting"
with open(resultsFile, 'wb') as f:
    o = csv.writer(f)
    for user in users:
        if user < 26541:
            continue
        print user
        edits = nT.getEdits(user, startDate, endDate)
        currStart = startDate
        currEnd = currStart + dT.timedelta(days=30)
        currIndex = 0
        while currIndex < len(edits):
            # Intialize list of active days
            activeDays = []
            allEdits = nT.getEditCount(user, currStart, currEnd, False)
            # Initialize dictionary
            # If we're past our date, then stop.
            if currStart > endDate:
                break
            # Go through each remaining edit, adding them to dictionary
            for i, edit in enumerate(edits[currIndex:]):
                if edit[1].date() <= currEnd:
                    activeDays.append(edit[1].date())
                # If it's after the current end, then don't record it.
                else:
                    # Correct i so that we don't miss the last edit
                    i -= 1
                    break
            # Add entry for number of active days
            days = len(set(activeDays))
            o.writerow([user,currStart,allEdits,days])
            cur = conn.cursor()
            cur.execute("""UPDATE userstats SET active_days = %s, all_edits = %s WHERE user_id = %s AND start_date = %s""", (days, allEdits, user, currStart))
            cur.close()
            conn.commit()
            # Update stuff for the next iteration
            currIndex += i + 1
            currStart = currEnd
            currEnd += dT.timedelta(days = 30)
