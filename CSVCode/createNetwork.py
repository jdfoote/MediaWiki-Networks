import sys
import networkTools as nT

def main():
	cutoff = 2
	editsDoc = sys.argv[1]
	placesDocs = [sys.argv[2],sys.argv[3],sys.argv[4]]
	dateStrings = [re.search('\d+', placesDoc).group(0) for placesDoc in placesDocs]
	watchDates = [datetime.datetime.strptime(dateString, '%Y%m%d') for dateString in dateStrings]
	print "Making watch Dicts"
	watchDicts = [nT.makeWatchDict(placesDoc) for placesDoc in placesDocs]
	print "Making edit Dicts"
	editorDicts = [nT.makeEditorDict(watchDicts[i], editsDoc, watchDates[i]) for i in range(len(watchDicts))]
	print "Making netork Dicts"
	networkDicts = [nT.makeNetwork(watchDicts[i], editorDicts[i]) for i in range(len(watchDicts))]

	print "Getting full nodes list"
	nodeList = getNodes(networkDicts, cutoff)
	print "Making matrix"
	finalMatrices = [nT.networkDictToBinaryMatrix(networkDict, nodeList, cutoff) for networkDict in networkDicts]
	for i, dateString in enumerate(dateStrings):
		with open('WeRelateMatrix{}.txt'.format(dateString), 'w') as f:
			for l in finalMatrices[i]:
	 			f.write(' '.join(l) + '\n')
	with open('NodeList.pkl', 'w') as f:
		pickle.dump(nodeList, f)
	


if __name__ == "__main__":
	main()
