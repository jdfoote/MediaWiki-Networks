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
collabDelta = dt.timedelta(days=config['collabDelta'])

obsMatrix = './Tests/obsMatrix.csv'
localCom = './Tests/localComMatrix.csv'
globalCom = './Tests/globalComMatrix.csv'
collabMatrix = './Tests/collabMatrix.csv'

def testGetSectionFromComment():
    testStrings = ['/* Test */', '/* Test1 */', '/* Test */ Doing some stuff', '/* Test */ [14 January 2012]', 'Test [14 January 2011]', 'Test [15 January 2010']
    sections = [nT.getSectionFromComment(x) for x in testStrings]
    assert sections[0] == sections[2] == sections[3] == sections[4] == 'Test'
    assert sections[0] != sections[1]
    assert sections[0] != sections[5]

def matrixComparison(csvMatrix, networkMatrix):
    for i, row in enumerate(networkMatrix):
        trueRow = csvMatrix.next()
        outputRow = [str(x) for x in row]
        if trueRow != outputRow:
            raise Exception('''ID {} doesn't match!\nCSV Row:{}\nTestRow:{}\n
            FullCSV:{}\nFullOutput:{}'''.format(i+1, trueRow, outputRow, csvMatrix, networkMatrix))

def observationTest():
    obsNetwork = nT.makeObservationNetwork(userList, startTime, endTime, 1)
    with open(obsMatrix, 'rb') as f:
        testMatrix = csv.reader(f, delimiter = ' ')
        matrixComparison(testMatrix, obsNetwork)

def localCommTest():
    localNetwork = nT.makeLocalCommNetwork(userList, startTime, endTime, commDelta, cutoff, userTalk, contentTalk)
    with open(localCom, 'rb') as f:
        testMatrix = csv.reader(f, delimiter = ' ')
        matrixComparison(testMatrix, localNetwork)

def globalCommTest():
    globalNet = nT.makeGlobalCommNetwork(userList, startTime, endTime, commDelta, cutoff, globalCats, complexPages)
    with open(globalCom, 'rb') as f:
        testMatrix = csv.reader(f, delimiter = ' ')
        matrixComparison(testMatrix, globalNet)

def collaborationTest():
    collabNet = nT.makeCollaborationNetwork(userList, startTime, endTime, collabDelta, cutoff)
    with open(collabMatrix, 'rb') as f:
        testMatrix = csv.reader(f, delimiter = ' ')
        matrixComparison(testMatrix, collabNet)

testGetSectionFromComment()
print "Comments retrieval passed"
observationTest()
print "Observation Test passed"
localCommTest()
print "Local Comm passed"
globalCommTest()
print "Global Comm passed"
collaborationTest()
print "Collaboration passed"
