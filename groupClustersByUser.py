import csv
import sys
from collections import defaultdict

'''
Takes a stats file that has user-months, and groups it by user instead.

Input file format is a CSV file, that must include at least the following columns:
user_id,all_edits,clusterType*

* This is defined by a variable


Outputs a CSV that looks like
id,T1,T2,T3 ....

Where each i,j is the cluster user i was at j months into their tenure.
The keepInactiveCount variable determines how many of months after their last activity should be kept.
'''

fullStats = sys.argv[1]
outputFile = sys.argv[2]
clusterType = 'kMedCluster'
# Identify whether to remove the last inactive months, and how many to keep
removeTrailingInactive = True
keepInactiveCount = 0

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
