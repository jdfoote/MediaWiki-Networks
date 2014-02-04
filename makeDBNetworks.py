import networkTools as nt
import datetime as dt
import csv
import yaml

networkTypes = ["observation", "localComm", "globalComm"]
nodeList = '/home/jeremy/Programming/WeRelate/DataFiles/WatchAndLearn/watchAndLearnNodes.csv'
saveLocation = '/home/jeremy/Programming/WeRelate/DataFiles/WatchAndLearn/'
with open('config.yaml', 'rb') as f:
    config = yaml.load(f)
startDate = config['startDate']
endDate = config['endDate']
delta = config['delta'] # Time between networks, in days
commDelta = config['commDelta'] # Max time between communication edits.
cutoffLevel = config['cutoff']
userTalkCats = config['userTalkCats']
contentTalkCats = config['contentTalkCats']
globalCats = config['globalCats']
complexPages = config['complexPages']

print "Connecting to DB..."

for networkType in networkTypes:
    with open(nodeList, 'rb') as i:
        nL = [int(x[0]) for x in csv.reader(i)]
        currStart = startDate
        while currStart <= endDate - delta:
            currEnd = currStart + delta
            if networkType == 'observation':
                currNetwork = nt.makeObservationNetwork(nL, currStart, currEnd, cutoff = cutoffLevel)
            elif networkType == 'localComm':
                currNetwork = nt.makeLocalCommNetwork(nL, currStart, currEnd, commDelta, cutoffLevel, userTalkCats, contentTalkCats)
            elif networkType == 'globalComm':
                currNetwork = nt.makeGlobalCommNetwork(nL, currStart, currEnd, commDelta, cutoffLevel, globalCats, complexPages)
            else:
                print 'Need to change the network type'
            with open('{}{}_{}.csv'.format(saveLocation, currStart.strftime('%Y_%m_%d'),networkType), 'wb') as o:
                print 'Writing {}'.format(currStart.strftime('%Y-%m-%d'))
                o.write(currNetwork)
            currStart = currEnd
