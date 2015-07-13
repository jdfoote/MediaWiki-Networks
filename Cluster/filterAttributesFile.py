import csv
import yaml
import sys
from datetime import datetime

# Takes in the stats file and filters by the node list and the start date.

statsFile, nodeFile, outputFile = sys.argv[1:4]
with open('config.yaml', 'rb') as f:
    config = yaml.load(f)
startDate = config['startDate']
endDate = config['endDate']


with open(nodeFile, 'rb') as g:
    nodeList = [x.rstrip() for x in g]
    print nodeList
with open(statsFile, 'rb') as f:
    stats = csv.reader(f)
    with open(outputFile, 'wb') as g:
        out = csv.writer(g)
        out.writerow(stats.next())
        for row in stats:
            currUser, currStart, currEnd = row[0], datetime.strptime(row[1], '%Y-%m-%d').date(), datetime.strptime(row[2], '%Y-%m-%d').date()
            if currUser in nodeList and currStart >= startDate and currEnd <= endDate:
                out.writerow(row)
