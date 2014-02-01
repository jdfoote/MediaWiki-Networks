import networkTools as nT
import csv

with open('../TestData/fakeDB.csv', 'rb') as o:
    f = csv.reader(o)
    f.next()
    db = [x for x in f]

def testGetSectionFromComment():
    testStrings = ['/* Test */', '/* Test1 */', '/* Test */ Doing some stuff', '/* Test */ [14 January 2012]', 'Test [14 January 2011]', 'Test [15 January 2010']
    sections = [nT.getSectionFromComment(x) for x in testStrings]
    assert sections[0] == sections[2] == sections[3] == sections[4] == 'Test'
    assert sections[0] != sections[1]
    assert sections[0] != sections[5]


testGetSectionFromComment()
