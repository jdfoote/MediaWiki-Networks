import networkTools as nt
import datetime as dt
import csv

networkTypes = ["observation", "localComm", "globalComm"]
nodeList = '/home/jeremy/Programming/WeRelate/DataFiles/WatchAndLearn/watchAndLearnNodes.csv'
saveLocation = '/home/jeremy/Programming/WeRelate/DataFiles/WatchAndLearn/'
startDate = dt.datetime(2012,07,03)
endDate = dt.datetime(2013,02,26)
delta = dt.timedelta(30) # Time between networks, in days
commDelta = dt.timedelta(7) # Max time between communication edits.
cutoffLevel = 1
userTalkCats = ['User talk']
contentTalkCats = ['Person talk','Image talk', 'Givenname talk', 'Surname talk', 'Place talk', 'Source talk', 'Family talk', 'MySource talk', 'Repository talk']
globalCats = ['Help talk', 'WeRelate talk', 'Template talk', 'Category talk']
complexPages = ['2031061', '2723696', '7242635']

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
