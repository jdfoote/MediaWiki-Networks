import networkTools as nt
import datetime as dt
import csv
import yaml

networkTypes = ["observation", "localComm", "globalComm", "collaboration"]
nodeList = '/home/jeremy/Programming/WeRelate/DataFiles/overFiveEditsForTwoMonthsStartBefore20120603.csv'
saveLocation = '/home/jeremy/Programming/WeRelate/DataFiles/ThesisNetworks/'
with open('config.yaml', 'rb') as f:
    config = yaml.load(f)
startDate = config['startDate']
endDate = config['endDate']
delta = dt.timedelta(days=config['timeDelta']) # Time between networks, in days
commDelta = dt.timedelta(days=config['commDelta']) # Max time between communication edits.
collabDelta = dt.timedelta(days=config['collabDelta']) # Max time between communication edits.
cutoffLevel = config['cutoffLevel']
userTalkCats = config['userTalkCats']
contentTalkCats = config['contentTalkCats']
globalCats = config['globalCats']
complexPages = config['complexPages']

print "Connecting to DB..."

for networkType in networkTypes:
    print "Starting {} networks".format(networkType)
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
            elif networkType == 'collaboration':
                currNetwork = nt.makeCollaborationNetwork(nL, currStart, currEnd, collabDelta, cutoff = cutoffLevel)
            else:
                print 'Need to change the network type'
            with open('{}{}_{}.csv'.format(saveLocation, currStart.strftime('%Y_%m_%d'),networkType), 'wb') as o:
                print 'Writing {}'.format(currStart.strftime('%Y-%m-%d'))
                output = csv.writer(o, delimiter = ' ')
                output.writerows(currNetwork)
            currStart = currEnd
