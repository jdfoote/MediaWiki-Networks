import csv
import sys
from collections import defaultdict

# Combines the full CSV of stats with the results from the clustering. The clustering results only show the months that had some activity, so a new cluster for very little activity is added.

# Assumes that both files are ordered the same, and that the IDS and start dates in clusterResults
# are a subset of those in fullStats

fullStats = sys.argv[1]
clusterResults = sys.argv[2]

with open(fullStats, 'rb') as f:
    with open(clusterResults, 'rb') as g:
        fs = csv.reader(f)
        # put header in results file
        results = [fs.next() + ['kMeansCluster', 'GMMCluster', 'kMedCluster']]
        cr = csv.DictReader(g)
        currCR = cr.next()
        for statrow in fs:
            # Check if this entry appears in the cluster results
            if currCR['start_date'] == statrow[1] and currCR['user_id'] == statrow[0]:
                currKMeans = currCR['kCluster']
                currGMM = currCR['mCluster']
                currKMed = currCR['kMedCluster']
                try:
                    currCR = cr.next()
                except:
                    continue
            else:
                currKMeans = currGMM = currKMed = 0
            results.append(statrow + [currKMeans, currGMM, currKMed])

with open(fullStats, 'wb') as f:
    output = csv.writer(f)
    for row in results:
        output.writerow(row)
