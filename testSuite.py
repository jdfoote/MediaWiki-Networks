import networkTools as nT
import csv
import datetime as dt

userList = [str(x) for x in range(50)]
startTime = dt.datetime(2012,12,01)
endTime = dt.datetime(2013,03,01)

def testGetSectionFromComment():
    testStrings = ['/* Test */', '/* Test1 */', '/* Test */ Doing some stuff', '/* Test */ [14 January 2012]', 'Test [14 January 2011]', 'Test [15 January 2010']
    sections = [nT.getSectionFromComment(x) for x in testStrings]
    assert sections[0] == sections[2] == sections[3] == sections[4] == 'Test'
    assert sections[0] != sections[1]
    assert sections[0] != sections[5]


def ObservationTest():
    obsNetwork = nT.makeObservationNetwork(userList, startTime, endTime, 1)


testGetSectionFromComment()
