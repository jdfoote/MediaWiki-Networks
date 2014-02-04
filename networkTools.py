import re
import csv
import datetime
import psycopg2
from collections import defaultdict
import yaml

with open('config.yaml', 'rb') as f:
    config = yaml.load(f)

conn = psycopg2.connect("dbname={} user=jeremy".format(config['database'])

def makeGlobalCommNetwork(userList, startTime, endTime, delta, cutoff, globalCats, complexPages):
    '''Each edit made by each user in the userlist is examined.

    For pages in the globalCats list (and not in the complexPages list), it adds a tie between
    the user in question and any editors who have edited in the last delta days (or since the
    user in question edited the page - whichever is shorter).

    For the complex pages, they must have edited the same section of the page (according to the
    comment)'''
    globalCommDict = {x:getGlobalComm(x, userList, startTime, endTime, delta, globalCats, complexPages) for x in userList}
    return networkDictToMatrix(globalCommDict, cutoff = cutoff, dichotomize=False)

def getGlobalComm(userID, userList, startTime, endTime, delta, globalCats, complexPages):
    '''For the user ID, returns a dictionary of all of the global comm partners'''
    edits = getEdits(userID, startTime, endTime)
    commDict = defaultdict(int)
    for edit in edits:
        pageID, editTime, pageCat, pageName, userName, comment = edit
        if pageCat in globalCats or pageID in complexPages:
            if pageID in complexPages:
                # If it's a complex page, then get only those who edited the same section (per the comment)
                commPartners = getComplexTalkers(userID, pageID, comment, editTime - delta, editTime)
            else:
                commPartners = getRecentEditors(userID, pageID, editTime - delta, editTime)
        else:
            commPartners = []
        for cp in commPartners:
            if cp != userID and cp in userList:
                commDict[cp] += 1
    return commDict

def makeLocalCommNetwork(userList, startTime, endTime, delta, cutoff, userTalkCats, contentTalkCats):
    '''Takes a list of users, a start time, and end time, a timedate delta (how far back to look 
    for edits) and a cutoff for dichotomizing the network. It also takes 2 lists - one for user 
    Talk categories, and one for content talk categories.

    Each edit made by each user in the userList is examined.
    For content talk pages, an undirected tie is created between the user in question, and any
    editors who have edited in the last delta days (or since the user in question edited
    the page - whichever is shorter).
    For user talk pages, edits that happen on the same page are recorded in the same way.
    However, if a user i edits user j's talk page, then we also check user i's talk page for +-
    delta days, to see if user j edited it.

    Returns an undirected, binary matrix'''
    localCommDict = {x:getLocalComm(x, userList, startTime, endTime, delta, userTalkCats, contentTalkCats) for x in userList}
    print max(localCommDict.values())
    return networkDictToMatrix(localCommDict, cutoff = cutoff,dichotomize=False)

def getLocalComm(userID, userList, startTime, endTime, delta, userTalkCats, contentTalkCats):
    '''For the user ID, returns a dictionary of all of the comm partners (in the
    userList), with how many times they communicated'''
    edits = getEdits(userID, startTime, endTime)
    commDict = defaultdict(int)
    for edit in edits:
        pageID, editTime, pageCat, pageName, userName, comment = edit
        if pageCat in userTalkCats:
            commPartners = getUserTalkers(userID, userName, pageID, pageName, editTime, delta)
        elif pageCat in contentTalkCats:
            commPartners = getRecentEditors(userID, pageID, editTime - delta, editTime)
        else:
            commPartners = []
        for cp in commPartners:
            if cp != userID and cp in userList:
                commDict[cp] += 1
    return commDict

def getComplexTalkers(userID, pageID, origComment, startTime, endTime):
    '''Takes info about a page, and returns a list of others who've edited the same
    section of the page in the given time period (or since the time the user
    last edited that section)'''
    # Get the section of the page
    origSec = getSectionFromComment(origComment)
    edits = getPageEdits(pageID, startTime, endTime)
    talkers = []
    for edit in edits:
        uID, editTime, comment = edit
        currSec = getSectionFromComment(comment)
        # Match if the comment is from the same section, or if it isn't from a section
        if not currSec or currSec == origSec:
        # Only get the edits since the last edit by this user (others will have been counted
        # when looking at that edit)
            if uID == userID:
                break
            else:
                talkers.append(uID)
    return set(talkers)



def getSectionFromComment(comment):
    '''Finds the section an edit was made to, based on the comment.

    The first edit to a section is formatted as "Section name [dd mon yyyy]".
    Subsequent edits are "/* Section name \* Comment here".
    If there is no section name, then return None.'''
    a = re.match(r'\/\* (.*) \*\/.*', comment)
    if a:
        return a.group(1)
    b = re.match(r'(.*) \[[^]]*\]$', comment)
    if b:
        return b.group(1)
    else:
        return None


def getUserTalkers(userID, userName, pageID, pageName, editTime, delta):
    '''For a given edit, returns a list of others who have either edited the same page in
    the last delta days before editTime, or had a conversation across pages.

    If the edit is on another user's page, it includes any edits made by
    the "owner" of this user page on the user talk page of the current user
    (to capture cross-page conversation)'''
    startTime = editTime - delta
    talkers = getRecentEditors(userID, pageID, startTime, editTime)
    pageOwner = pageName[10:]
    pageOwnerID = getUserID(pageOwner)
    # If the page owner isn't already in the list of talkers, see if he/she has edited
    # the current users' page
    if userName != pageOwner and pageOwnerID not in talkers:
        # Get the current user's page ID
        usersPageName = 'User talk:{}'.format(userName)
        userPageID = getPageID(usersPageName)
        # Get the last edit made by the current user on this page (to avoid double counting)
        lastEdit = getLastEditByUser(userID, pageID, startTime, editTime)
        # If there was an edit by the current user on this page, then only get edits from
        # his page that are after that time.
        startTime = lastEdit if lastEdit else startTime
        usersPageEditors = getRecentEditors(userID, userPageID, startTime, editTime)
        # If the other person edited the current user's page in the given time period,
        # then add them as a co-communicator
        if pageOwnerID in usersPageEditors:
            talkers |= pageOwnerID
    return talkers

def getUserID(userName):
    cur = conn.cursor()
    cur.execute("""SELECT user_id from users WHERE user_name = %s;""", (userName,))
    uid = cur.fetchone()
    cur.close()
    return uid

def getPageID(pageName):
    cur = conn.cursor()
    cur.execute("""SELECT page_id from pages WHERE page_name = %s;""", (pageName,))
    pid = cur.fetchone()
    cur.close()
    return pid

def getLastEditByUser(userID, pageID, startTime, endTime):
    '''Gets the most recent (non-automated) edit by a given user on a given page, after
    the startTime, and before the endTime'''
    cur = conn.cursor()
    cur.execute("""SELECT edit_time from non_bot_edits WHERE
            user_id = %s AND page_id = %s AND edit_time < %s AND edit_time > %s
            ORDER BY edit_time DESC;""", (userID, pageID, startTime, endTime))
    lastEdit = cur.fetchone()
    cur.close()
    # Return the result. Or, if there is no result, return the 
    result = lastEdit if lastEdit else startTime
    return result

def getRecentEditors(userID, pageID, startTime, endTime):
    '''Figures out which editors have edited a page between the start time and end time,
    as long as userID hasn't edited since their edit. Returns a set of ids'''
    uids = []
    editors = getPageEdits(pageID, startTime, endTime)
    # Return all of the editors who edited since the last time the current userID edited the page
    for e in editors:
        if e[0] == userID:
            break
        else:
            uids.append(e[0])
    return set(uids)

def getPageEdits(pageID, startTime, endTime):
    '''Takes a page ID, returns all of the edits that occurred between the start time and end time'''
    cur = conn.cursor()
    cur.execute("""SELECT user_id, edit_time, comment from non_bot_edits WHERE page_id = %s
            AND edit_time > %s AND edit_time < %s
            ORDER BY edit_time DESC;""", (pageID, startTime, endTime))
    edits = cur.fetchall()
    return edits

def makeObservationNetwork(userList, startTime, endTime, cutoff):
    '''Takes a list of users of interest, a start time, an end time, and a cutoff (integer).
    Returns a directed, binary network matrix, where X(ij) = 1 if j was the last editor of
    a page that i edited between the start and end dates (and if i!=j).'''
    observationDict = {x:getObservations(x, startTime, endTime, userList) for x in userList}
    return networkDictToMatrix(observationDict, cutoff = cutoff, dichotomize = False)

def getObservations(userID, startTime, endTime, userList):
    '''Takes a userID, startTime, endTime, and userList. Returns a dictionary of the form
    {userID1: count, ....}. Count is the number of times that each userID was the last editor of
    a page that the the focal user edited between the startTime and endTime.'''
    edits = getEdits(userID, startTime, endTime)
    observationsDict = defaultdict(int)
    for edit in edits:
        observed = getLastEditor(edit[0], edit[1])
        if observed != userID and observed in userList:
            observationsDict[observed] += 1
    return observationsDict


def getEdits(userID, startTime, endTime, nonBot = True):
    '''Takes a user ID, and 2 times, and returns a list of tuples
    for each edit made by that user in that time period, from oldest to newest'''
    cur = conn.cursor()
    if nonBot == True:
        cur.execute("""SELECT page_id, edit_time, page_category, page_name, user_name, comment FROM
            non_bot_edits WHERE user_id = %s AND edit_time > %s
            AND edit_time < %s ORDER BY edit_time ASC;""", (userID, startTime, endTime))
    else:
        cur.execute("""SELECT page_id, edit_time, page_category, page_name, user_name, comment FROM
            temp_edits WHERE user_id = %s AND edit_time > %s
            AND edit_time <= %s ORDER BY edit_time ASC;""", (userID, startTime, endTime))
    edits = cur.fetchall()
    cur.close()
    return edits

def getEditCount(userID, startTime, endTime, nonBot = True):
    '''Takes a user ID, and 2 times, and returns how many edits were made
    by that user in that time period'''
    cur = conn.cursor()
    if nonBot == True:
        cur.execute("""SELECT COUNT(*) FROM
            non_bot_edits WHERE user_id = %s AND edit_time > %s
            AND edit_time < %s;""", (userID, startTime, endTime))
    else:
        cur.execute("""SELECT COUNT(*) FROM
            temp_edits WHERE user_id = %s AND edit_time > %s
            AND edit_time < %s;""", (userID, startTime, endTime))
    edits = cur.fetchone()[0]
    cur.close()
    return edits

def getActiveUsers(startTime, endTime):
    '''Get a list of all users who have made an edit during the given time period'''
    cur = conn.cursor()
    cur.execute("""SELECT user_id, first_edit, last_edit from users ORDER BY user_id ASC;""")
    allUsers = cur.fetchall()
    cur.close()
    activeUsers = []
    for u in allUsers:
        uid, firstEd, lastEd = u
        if firstEd > endTime:
            break
        elif firstEd < startTime:
            if lastEd > startTime:
                activeUsers.append(uid)
        else:
            activeUsers.append(uid)
    return activeUsers



def getLastEditor(pageID, editTime):
    '''Takes a pageID and an editTime, and returns the user id of the person who last edited
    the page'''
    cur = conn.cursor()
    cur.execute("""SELECT user_id from non_bot_edits WHERE page_id = %s
            AND edit_time < %s
            ORDER BY edit_time DESC;""", (pageID, editTime))
    edit = cur.fetchone()
    uid = edit[0] if edit else None
    cur.close()
    return uid

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

def networkDictToMatrix(nDict, nodeList=[], cutoff=1, dichotomize=True):
    '''Takes a dictionary in the format {watcher: {editor: count,...},...}, a list of nodes of 
    interest, and a cutoff point. Returns a binary matrix of watchers, in the format
    0 0 0 0 1 0 1
    1 1 0 0 0 0 1
    where ij represented a directed relationship between i and j of that strength.'''
    if not nodeList:
        nodeList = sorted(nDict)
    finalMatrix = []
    for i in nodeList:
        iRow = []
        for j in nodeList:
            if i in nDict and j in nDict[i] and nDict[i][j] >= cutoff:
                if dichotomize:
                    iRow.append('1')
                else:
                    iRow.append(str(nDict[i][j]))
            else:
                iRow.append('0')
        finalMatrix.append(iRow)
    return listsToMatrix(finalMatrix)

def listsToMatrix(lists):
    '''Takes a list of lists, and changes it to a string-based matrix'''
    finalString = ''
    for l in lists:
        currString = ''
        for i in l:
            currString += i + ' '
        finalString += currString[:-1] + '\n'
    return finalString
