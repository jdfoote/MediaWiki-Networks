import csv
import sys
from collections import defaultdict

'''Takes a file with lists of clusters, and computes a number of stats.

----- Expected Format ------
Header row:
ID,T1Cluster,T2Cluster,T3Cluster....
A4,1,1,3,.....

The numPrevious variable determines how many previous measures to look at when
calculating stats. For example, if numPrevious = 2, then the example above would
have a stat for (1,1) -> 3, but if numPrevious = 1, then it would have a stat for
(1,) -> 1 and (1,) -> 3.

It prints a Latex code that can be inserted in the tabular environment. Changing the final line changes the format'''

roleDict = {'0': 'Low Activity', '1':'Central Member', '2':'Peripheral Expert', '3':'Newbie', 'NA': 'Leaving'}
numPrevious = 1
inputFile = sys.argv[1]
with open(inputFile, 'rb') as f:
    userClusters = csv.reader(f)
    # Skip header
    userClusters.next()
    results = defaultdict(int)
    # Go through each cluster and iterate results[(x,y)] whenever cluster x
    # is preceded by cluster y in the data.
    for row in userClusters:
        # Remove ID
        clusters = row[1:]
        # Start with the numPrevious cluster, then look backward at what preceded each cluster
        for i in range(numPrevious,len(clusters)):
            lastClus, currClus = tuple(clusters[i-numPrevious:i]), clusters[i]
            results[(lastClus, currClus)] += 1

results = sorted([(k,v) for k,v in results.iteritems()])

totObs = float(sum(r[1] for r in results))
for r in results:
    obs = r[1]
    # Calculate how many observations have the same previous clusters
    currPreviousObs = float(sum(x[1] for x in results if x[0][0] == r[0][0]))
    lc = ','.join([roleDict[c] for c in r[0][0]])
    print "{} & $\\rightarrow$ & {} & {} & {:.2f}\\% & {:.2f}\\%\\\\".format(lc,roleDict[r[0][1]],obs,obs*100/totObs, obs*100/currPreviousObs)

for r in results:
    lc = ','.join([roleDict[c] for c in r[0][0]])
    print "{}\t{}\t{}".format(lc,roleDict[r[0][1]],r[1])
