import csv
import sys
from collections import defaultdict

# Takes a stats file that has user-months, and groups it by user instead.
# Outputs a CSV that looks like 
# UserID  T1  T2  T3 ....
# Where each T is the cluster the user was at that many months into their tenure.
# The final months where they were inactive can be optionally removed

fullStats = sys.argv[1]
outputFile = sys.argv[2]
clusterType = 'kMedCluster'
# Identify whether to remove the last inactive months, and how many to keep
removeTrailingInactive = True
keepInactiveCount = 3

with open(fullStats, 'rb') as f:
    fs = csv.DictReader(f)
    # Initialize variables
    allClusters = []
    currClusters = []
    isActive = []
    currUser = ''
    for statrow in fs:
        userID = statrow['user_id']
        edits = int(statrow['all_edits'])
        if userID == currUser:
            currClusters.append(statrow[clusterType])
            isActive.append(edits > 0)
        else:
            # If it's a new user ID, then append the old one to the results, and reset
            if currClusters:
                if removeTrailingInactive:
                    # Remove all the trailing inactive records
                    while isActive.pop() == False:
                        continue
                    # Add back the last popped item, plus the keepInactiveCount
                    currClusters = currClusters[:len(isActive) + 2 + keepInactiveCount]

                allClusters.append(currClusters)
            currUser = userID
            currClusters = [userID, statrow[clusterType]]
            isActive = [edits > 0]
    # Append the final cluster, which won't have been caught.
    allClusters.append(currClusters)

with open(outputFile, 'wb') as f:
    output = csv.writer(f)
    # Figure out how many columns there should be
    maxTime = max([len(x) for x in allClusters]) - 1
    header = ['id'] + ['T{}'.format(x) for x in range(1, maxTime + 1)]
    output.writerow(header)
    for row in allClusters:
        output.writerow(row)