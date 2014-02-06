
#from xml.etree.ElementTree import iterparse
def makeWatchDict(placesDoc):
    '''Takes a TSV watchlist in the format user\tnamespace\tpage, and returns a dictionary
    in the format {page:[user 1,user 2,...]...}'''
    with open(placesDoc, 'rb') as csvfile:
        f = csv.reader(csvfile,delimiter='\t')
        watchDict = {}
        for row in f:
            userID, ns, page = row
            if ns == '106':
                if page in watchDict:
                    # Add the person watching to the page
                    watchDict[page].append(userID)
                else:
                    watchDict[page] = [userID]
    return watchDict

def makeEditorDict(watchDict, editsDoc, endDate):
    with open(editsDoc, 'rb') as csvfile:
        f = csv.reader(csvfile, delimiter=',')
        idsToIgnore = ["0","48",'']
        editorDict = {}
        #Skip header
        f.next()
        for row in f:
            pageTitle = row[1]
            contributor = row[3]
            revDate = datetime.datetime.strptime(row[5], '%Y%m%d%H%M%S')
            if contributor not in idsToIgnore and revDate < endDate and pageTitle in watchDict:
                if pageTitle in editorDict:
                    editorDict[pageTitle].add(contributor)
                #    print pageTitle, editorDict[pageTitle]
                else:
                    editorDict[pageTitle] = set([contributor,])
    return editorDict

def makeNetwork(watchDict, editorDict):
    networkDict = {}
    for page in editorDict:
        for watcher in watchDict[page]:
#            print watcher
            if watcher not in networkDict:
                networkDict[watcher] = {editor: 1 for editor in editorDict[page] if editor != watcher}
            else:
                for editor in editorDict[page]:
                    if editor != watcher:
                        networkDict[watcher][editor] = networkDict[watcher].get(editor, 0) + 1
                        if editor not in networkDict:
                            networkDict[editor] = {}

    return networkDict

def getNodes(networkDicts, cutoff):
    nodes = set([])
    for network in networkDicts:
        for watcher in network:
            for editor in network[watcher]:
                if network[watcher][editor] >= cutoff:
                    nodes.add(watcher)
                    nodes.add(editor)
    return sorted(list(nodes))
