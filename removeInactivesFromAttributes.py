import csv
import sys
from collections import defaultdict

'''
Takes a stats file that has user-months, identifies the last month someone was active,
and removes any superfluous months.

Input file format is a CSV file, that must include at least the following columns, in
this order:

----- INPUT -----
user_id, start_date, end_date, all_edits,...


Outputs a CSV that changes the date into the number of months since joining,
and removes rows after they have quit.

-----OUTPUT----
id,month,att1,att2,...
1,0,X,Y
1,1,X,Z
...

The keepInactiveCount variable determines how many of months after their last activity should be kept.
'''

fullStats = sys.argv[1]
outputFile = sys.argv[2]
# Identify whether to remove the last inactive months, and how many to keep
removeInactive = True
keepInactiveCount = 0

def filterUser(activityList, isActive):
    # If the user was active in the last month, then they haven't quit, and inactive
    # months don't need to be removed
    if isActive[-1]:
        return activityList
    else:
        if removeInactive:
            # Remove all the trailing inactive records
            while isActive.pop() == False:
                continue
        # Add back the last popped item, plus the keepInactiveCount
        activityList = activityList[:len(isActive) + 1 + keepInactiveCount]
        return activityList

with open(fullStats, 'rb') as f:
    with open(outputFile, 'wb') as g:
        fs = csv.reader(f)
        output = csv.writer(g)
        # Write the header row
        output.writerow(fs.next())
        # Initialize variables
        currUserStats = []
        isActive = []
        currUser = ''
        currCount = 0
        for statrow in fs:
            userID = statrow[0]
            edits = int(statrow[3])
            if userID == currUser:
                statrow[1] = currCount
                currUserStats.append(statrow)
                isActive.append(edits > 0)
                currCount += 1
                #print currUserStats[currCount]
            else:
                # If it's a new user ID, then append the old one to the results, and reset
                if currUserStats:
                    currUserStats = filterUser(currUserStats, isActive)
                    #print currUserStats
                    output.writerows(currUserStats)
                currUser = userID
                currCount = 0
                statrow[1] = currCount
                currUserStats = [statrow]
                isActive = [edits > 0]
        # Append the final cluster, which won't have been caught.
        output.writerows(filterUser(currUserStats, isActive))
