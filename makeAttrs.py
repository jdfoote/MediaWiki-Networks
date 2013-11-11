import sys
import datetime
import pickle
import lxml.etree as ET

def makeAttrMatrices(editFile, nodeList, watchDates):
	'''Takes a list of nodes of interest, and returns a list of 4 longitudinal matrices, in the format
	[[[overallActivityT1P1, overallActivityT2P1],[overallActivityT1P2, overallActivityT2P2]],[[overallRecentT1P1,
	...],[overallRecentT1P2, ...]],...] where the other two are placesActivity and placesRecent'''
	watchDates = [datetime.datetime.strptime(w, '%Y%m%d') for w in watchDates]
	nodeDict = {n:[0]*4*len(watchDates) for n in nodeList}
	numDates = len(watchDates)
	NS = '{http://www.mediawiki.org/xml/export-0.3/}'
	with open(editFile, 'rb') as f:
		for event, elem in ET.iterparse(f):
			if elem.tag == '{0}page'.format(NS):
				t = elem.find("{0}title".format(NS))
				if t is not None:
					pageTitle = t.text
				e = elem.findall(".//{0}contributor/{0}id".format(NS))
				if e is not None:
					editors = [a.text for a in e]
				r = elem.findall(".//{0}timestamp".format(NS))
				if r:
					revDates = [a.text for a in r]
				for i in range(len(editors)):
					editor = editors[i]
					dateString = revDates[i]
					if editor in nodeDict:
						revDate = datetime.datetime.strptime(dateString, '%Y-%m-%dT%H:%M:%SZ')
						isPlace = True if pageTitle[0:6]=='Place:' else False
						for i in range(numDates):
							if revDate < watchDates[i]:
								nodeDict[editor][i]+=1
								if isPlace:
									print "oldPlace"
									nodeDict[editor][i+numDates*2]+=1
								if revDate > watchDates[i] - datetime.timedelta(days=30):
									nodeDict[editor][i+numDates]+=1
									if isPlace:
										print "newPlace"
										nodeDict[editor][i+numDates*3] += 1
				elem.clear()
	finalMatrices = [[],[],[],[]]
	for n in nodeList:
		nodeStats = nodeDict[n]
		for i in range(4):
			finalMatrices[i].append(nodeStats[i*numDates:(i+1)*numDates])
	return finalMatrices

def testThis(nodeList, nodeDict, numDates):
	finalMatrices = [[],[],[],[]]
	for n in nodeList:
		nodeStats = nodeDict[n]
		for i in range(4):
			finalMatrices[i].append(nodeStats[i*numDates:(i+1)*numDates])
	print finalMatrices

		
def main():
	nodeFile = sys.argv[1]
	editFile = sys.argv[2]
	watchDates = ['20120906', '20121013', '20121201']
	fileNames = ['allActivity.dat', 'recentOverall.dat', 'allPlaces.dat', 'recentPlaces.dat']
	with open(nodeFile, 'r') as f:
		nodeList = pickle.load(f)
	print len(nodeList)
	attMatrices = makeAttrMatrices(editFile, nodeList, watchDates)
	for i in range(len(fileNames)):
		with open(fileNames[i], 'wb') as f:
			for p in attMatrices[i]:
				f.write(' '.join(str(x) for x in p) + '\n')

#testThis([1,4,5,6],{1:[4,5,7,1,2,4,6,8,9,5,3,3], 4:[3]*12, 5:[5]*5 + [4,5,6,7,8,9,12], 6:[1,2,3,4,5,6,7,8,9,1,11,12]}, 3)

if __name__ == "__main__":
	main()
