import csv
import sys
from collections import defaultdict

# Combines the full CSV of stats with the results from the clustering. The clustering results only show the months that had some activity, so a new cluster for very little activity is added.

fullStats = sys.argv[1]
clusterResults = sys.argv[2]

with open(fullStats, 'rb') as f:
    with open(clusterResults, 'rb') as g:
        fs = csv.reader(f)
        # put header in results file
        results = [fs.next() + ['kMeansCluster', 'GMMCluster']]
        cr = csv.DictReader(g)
        kMeansCount = defaultdict(int)
        GMMCount = defaultdict(int)
        currUser = ''
        lastKMeans = ''
        lastGMM = ''
        currCR = cr.next()
        for statrow in fs:
            # Check if this entry appears in the cluster results
            if currCR['start_date'] == statrow[1] and currCR['user_id'] == statrow[0]:
                currKMeans = currClusterRow['kClusters']
                currGMM = currClusterRow['mClusters']
                currCR = cr.next()
            else:
                currKMeans = 0
                currGMM = 0
            results.append(statrow + [currKMeans, currGMM])

with open(fullStats, 'wb') as f:
    output = csv.writer(f)
    for row in results:
        output.writerow(row)

            # Check if we're still dealing with the same user
#            if statrow[0] == currUser:
#                # Check if there's an entry in cr
#                currIndex = crIndex
#                currKMeans = ''
#                currGMM = ''
#                while cr[currIndex]['user_id'] = currUser:
#                        break
#                    else:
#                        currIndex += 1
#

