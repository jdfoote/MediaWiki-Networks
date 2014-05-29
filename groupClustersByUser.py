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
removeInactive = True
keepInactiveCount = 0
# For the stats, this identifies the month that a user quit with "NA"
NAForLastMonth = True

def filterUser(clusterList, isActive):
    # If the user was active in the last month, then they haven't quit, and inactive
    # months don't need to be removed
    if isActive[-1]:
        return clusterList
    else:
        if removeInactive:
            # Remove all the trailing inactive records
            while isActive.pop() == False:
                continue
        # Add back the last popped item, plus the userID, plus the keepInactiveCount and the NA (if needed)
        clusterList = clusterList[:len(isActive) + 2 + keepInactiveCount] + ['NA'] * NAForLastMonth
        return clusterList

assert filterUser(['id',1,2,3,0,0],[True,True,True,False,False]) == ['id',1,2,3,'NA']

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
                currClusters = filterUser(currClusters, isActive)
                allClusters.append(currClusters)
            currUser = userID
            currClusters = [userID, statrow[clusterType]]
            isActive = [edits > 0]
    # Append the final cluster, which won't have been caught.
    allClusters.append(filterUser(currClusters, isActive))

with open(outputFile, 'wb') as f:
    output = csv.writer(f)
    # Figure out how many columns there should be
    maxTime = max([len(x) for x in allClusters]) - 1
    header = ['id'] + ['T{}'.format(x) for x in range(1, maxTime + 1)]
    output.writerow(header)
    for row in allClusters:
        output.writerow(row)
