import networkTools as nT
import csv
import datetime as dt
import yaml

with open('config.yaml', 'rb') as f:
    config = yaml.load(f)

userList = [x for x in range(1,30)]
startTime = dt.datetime(2012,12,01)
endTime = dt.datetime(2013,03,01)
cutoff = config['cutoffLevel']
userTalk = config['userTalkCats']
contentTalk = config['contentTalkCats']
globalCats = config['globalCats']
complexPages = config['complexPages']
commDelta = dt.timedelta(days=config['commDelta'])

def testGetSectionFromComment():
    testStrings = ['/* Test */', '/* Test1 */', '/* Test */ Doing some stuff', '/* Test */ [14 January 2012]', 'Test [14 January 2011]', 'Test [15 January 2010']
    sections = [nT.getSectionFromComment(x) for x in testStrings]
    assert sections[0] == sections[2] == sections[3] == sections[4] == 'Test'
    assert sections[0] != sections[1]
    assert sections[0] != sections[5]


def observationTest():
    obsNetwork = nT.makeObservationNetwork(userList, startTime, endTime, 1)
#    print obsNetwork

def localCommTest():
    commNetwork = nT.makeLocalCommNetwork(userList, startTime, endTime, commDelta, cutoff, userTalk, contentTalk)
#    print commNetwork

def globalCommTest():
#    print globalCats
    globalNet = nT.makeGlobalCommNetwork(userList, startTime, endTime, commDelta, cutoff, globalCats, complexPages)
#    print globalNet

testGetSectionFromComment()
observationTest()
localCommTest()
globalCommTest()
