import csv
import sys
from collections import defaultdict

inputFile = sys.argv[1]
with open(inputFile, 'rb') as f:
    userClusters = csv.reader(f)
    # Skip header
    userClusters.next()
    results = defaultdict(int)
    # Go through each cluster (reversed) and iterate results[(x,y)] whenever cluster x
    # is preceded by cluster y in the data.
    for row in userClusters:
        # Remove ID
        clusters = row[1:]
        # Start with the second cluster, then look backward at what preceded each cluster
        for i in range(1,len(clusters)):
            lastClus, currClus = clusters[i-1], clusters[i]
            results[(lastClus, currClus)] += 1

for r in results:
    print "{}\t{}\t{}".format(r[0],r[1],results[r])
