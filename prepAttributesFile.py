import csv
import yaml
import sys

# Takes in the stats file and filters by the node list.

statsFile, nodeFile, outputFile = sys.argv[1:4]


with open(nodeFile, 'rb') as g:
    nodeList = [x.rstrip() for x in g]
    print nodeList
with open(statsFile, 'rb') as f:
    stats = csv.reader(f)
    with open(outputFile, 'wb') as g:
        out = csv.writer(g)
        out.writerow(stats.next())
        for row in stats:
            if row[0] in nodeList:
                out.writerow(row)
