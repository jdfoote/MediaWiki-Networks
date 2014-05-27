import re
import csv
import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
from collections import defaultdict
import yaml

with open('./config.yaml', 'rb') as f:
    config = yaml.load(f)

conn = psycopg2.connect("dbname={} user={}".format(config['database'], config['user']))

def makeCollaborationNetwork(userList, startTime, endTime, delta, cutoff):
    '''Takes a list of users of interest, a start time, an end time, and a cutoff (integer).
    Returns an undirected, weighted network matrix, where X(ij) is
    increased by 1 if i and j made alternating edits within the last
    delta days, such that at least one edit by j occurred between two
    edits made by i.'''
    collaborationDict = {x:getCollaborators(x, startTime, endTime, delta, userList) for x in userList}
    return networkDictToMatrix(collaborationDict, cutoff = cutoff, dichotomize = False, directed = False)

def getCollaborators(userID, startTime, endTime, delta, userList):
    '''Takes a userID, startTime, endTime, and userList. Returns a dictionary of the form
    {userID1: count, ....}. Count is the number of collaborations
    that the two users made alternating edits within the last delta days.
    '''
    edits = getEdits(userID, startTime, endTime)
    collaboratorsDict = defaultdict(int)
    for edit in edits:
        pageID, editTime, pageCat, pageName, userName, comment = edit
        # Talk pages don't count as collaboration
        if pageCat[-4:] == 'talk':
            continue
        partners = [x[0] for x in getPageEdits(pageID, editTime - delta, editTime)]
        # See if the user edited the page in the past. If so, include everyone else as collaborators.
        collaborators = []
        for partner in partners:
            if partner == userID:
                for collaborator in collaborators:
                    collaboratorsDict[collaborator] += 1
                break
            else:
                collaborators.append(partner)
    return collaboratorsDict

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

def makeGlobalCommNetwork(userList, startTime, endTime, delta, cutoff, globalCats, complexPages):
    '''Each edit made by each user in the userlist is examined.

    For pages in the globalCats list (and not in the complexPages list), it adds a tie between
    the user in question and any editors who have edited in the last delta days (or since the
    user in question edited the page - whichever is shorter).

    For the complex pages, they must have edited the same section of the page (according to the
    comment)'''
    globalCommDict = {x:getGlobalComm(x, userList, startTime, endTime, delta, globalCats, complexPages) for x in userList}
    return networkDictToMatrix(globalCommDict, cutoff = cutoff, dichotomize=False, directed = False)

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
    return networkDictToMatrix(localCommDict, cutoff = cutoff,dichotomize=False, directed = False)

def getLocalComm(userID, userList, startTime, endTime, delta, userTalkCats, contentTalkCats):
    '''For the user ID, returns a dictionary of all of the comm partners (in the
    userList), with how many times they communicated'''
    edits = getEdits(userID, startTime, endTime)
    commDict = defaultdict(int)
    for edit in edits:
        pageID, editTime, pageCat, pageName, userName, comment = edit
        if pageCat in userTalkCats:
            commPartners = getUserTalkers(userID, userName, pageID, pageName, editTime, delta, comment)
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
        # Match if the comment is from the same section, or if either edit doesn't have a section
        if not currSec or not origSec or currSec == origSec:
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
    if comment:
        a = re.match(r'\/\* (.*) \*\/.*', comment)
        if a:
            return a.group(1).rstrip()
        b = re.match(r'(.*)\[[^]]*\]$', comment)
        if b:
            return b.group(1).rstrip()
    return None


def getUserTalkers(userID, userName, pageID, pageName, editTime, delta, comment):
    '''For a given edit, first gets a list of others who have edited the same section
    of this page in the last delta days before editTime.

    If the edit is on another user's page, it adds the owner of this page, if
    the "owner" of this user page has edited the user's talk page within the period of
    interest (to capture cross-page conversation)'''
    startTime = editTime - delta
    talkers = getComplexTalkers(userID, pageID, comment, startTime, editTime)
    pageOwner = pageName[10:]
    pageOwnerID = getUserID(pageOwner)
    # If the page owner (call him Oscar) isn't already in the list of talkers, see if he/she has edited
    # the current users' (Carl) page
    if userName != pageOwner and pageOwnerID and pageOwnerID not in talkers:
        # Get the Carl's page ID
        usersPageName = 'User talk:{}'.format(userName)
        userPageID = getPageID(usersPageName)
        # Get the last edit made by the Carl on Oscar's page (to avoid double counting)
        lastEdit = getLastEditByUser(userID, pageID, startTime, editTime)
        # If there was an edit by Carl on this page, then only get edits from
        # his page that are after that time.
        startTime = lastEdit if lastEdit else startTime
        # Get all of the edits from Carl's page
        usersPageEdits = getPageEdits(userPageID, startTime, editTime)
        # If the Oscar edited Carl's page in the given time period,
        # then add him as a co-communicator
        for edit in usersPageEdits:
            if edit[0] == pageOwnerID:
                # If Carl editited his own page within the delta days after Oscar
                # edited Carl's page, then this communication will already be counted, so
                # we should ignore it
                userPageEnd = edit[1] + delta
                if not getLastEditByUser(userID, userPageID, edit[1], userPageEnd):
                    talkers.add(pageOwnerID)
                    # Once we've found one communication, we don't need to keep looking
                    break
    return talkers

def getUserID(userName):
    cur = conn.cursor()
    cur.execute("""SELECT user_id from users WHERE user_name = %s;""", (userName,))
    uid = cur.fetchone()
    cur.close()
    if not uid:
        # print "User name {} not found!".format(userName)
        return None
    return uid[0]

def getPageID(pageName):
    cur = conn.cursor()
    cur.execute("""SELECT page_id from pages WHERE page_name = %s;""", (pageName,))
    pid = cur.fetchone()
    cur.close()
    return None if not pid else pid[0]

def getLastEditByUser(userID, pageID, startTime, endTime):
    '''Gets the time of the most recent (non-automated) edit by a given user on a given page, after
    the startTime, and before the endTime. Returns None if there is no edit'''
    cur = conn.cursor()
    cur.execute("""SELECT edit_time from non_bot_edits WHERE
            user_id = %s AND page_id = %s AND edit_time > %s AND edit_time < %s
            ORDER BY edit_time DESC;""", (userID, pageID, startTime, endTime))
    lastEdit = cur.fetchone()
    cur.close()
    # Return the result. Or, if there is no result, return the start time
    result = None if not lastEdit else lastEdit[0]
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
    cur.execute("""SELECT DISTINCT(user_id) from temp_edits WHERE edit_time > %s
            AND edit_time < %s;""", (startTime, endTime))
    allUsers = cur.fetchall()
    cur.close()
    if allUsers:
        return sorted([a[0] for a in allUsers])
    else:
        return None

def getUserActivityDates(userID):
    '''Returns the first edit and last edit dates for a user'''
    cur = conn.cursor()
    cur.execute("""SELECT first_edit, last_edit FROM users WHERE user_id = %s;""", (userID,))
    dates = cur.fetchone()
    return dates

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


def networkDictToMatrix(nDict, nodeList=[], cutoff=1, dichotomize=True, directed = True):
    '''Takes a dictionary in the format {watcher: {editor: count,...},...}, a list of nodes of 
    interest, and a cutoff point. Returns a binary matrix of watchers, in the format
    0 0 0 0 1 0 1
    1 1 0 0 0 0 1
    where ij represented a directed relationship between i and j of that strength.'''
    if not nodeList:
        nodeList = sorted(nDict.keys())
    finalMatrix = []
    for i in nodeList:
        iRow = []
        for j in nodeList:
            if i in nDict and j in nDict[i]:
                iRow.append(nDict[i][j])
            else:
                iRow.append(0)
        finalMatrix.append(iRow)
    if not directed:
        finalMatrix = directedToUndirected(finalMatrix)
    if dichotomize:
        finalMatrix = dichotomize(finalMatrix)
    return finalMatrix


def directedToUndirected(matrix, combinationFunction = lambda x, y: x+y):
    '''Takes a directed matrix (in the form of lists of lists), and applies the combination
    function (by default, a sum of both values). The result is then put in both X(i,j) and
    X(j,i).'''
    # Make sure it's a square
    if len(matrix) != len(matrix[0]):
        raise Exception("Not a square matrix!")
    for i in range(len(matrix)):
        for j in range(i+1):
            # For each edge, apply the combination function, and edit in place
            result = combinationFunction(matrix[i][j], matrix[j][i])
            matrix[i][j] = matrix[j][i] = result
    return matrix

def dichotomize(matrix, cutoff):
    '''Takes a directed matrix (in the form of lists of lists), and makes it a binary
    matrix, replacing everything equal to or greater than the cutoff with a '1', and everything
    under with a '0' '''
    # Make sure it's a square
    if len(matrix) != len(matrix[0]):
        raise Exception("Not a square matrix!")
    for i in range(len(matrix)):
        for j in range(len(matrix)):
            matrix[i][j] = min(matrix[i][j],1)
    return matrix

##### Statistics #########


def getStats(user, startDate, cats, otherStats):
    '''Takes a userID, a startDate, the name of the behavior variable, and a dictionary of lists 
    of categories. Returns a dictionary of each of the stats, with the categories condensed'''
    cur = conn.cursor(cursor_factory = RealDictCursor)
    cur.execute("""SELECT * from userstats WHERE user_id = %s AND start_date = %s;""",
            (user, startDate))
    stats = cur.fetchone()
    cur.close()
    results = {c:0 for c in cats}
    # For each statistic, check which category it should be in
    for stat in stats:
        found = False
        if stat in otherStats:
            found = True
            results[stat] = stats[stat]
            continue
        for cat in cats:
            if stat in cats[cat]:
                results[cat] += stats[stat]
                found = True
                break
        # Make sure there aren't surprises
        if found == False:
            raise Exception("{} not in {}".format(stat, cats))

    return results
