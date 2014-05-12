import csv
import sys
from collections import defaultdict

numPrevious = 2
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
        # Start with the numPrevious cluster, then look backward at what preceded each cluster
        for i in range(numPrevious,len(clusters)):
            lastClus, currClus = tuple(clusters[i-numPrevious:i]), clusters[i]
            results[(lastClus, currClus)] += 1

for r in results:
    print "{}\t{}\t{}".format(r[0],r[1],results[r])
