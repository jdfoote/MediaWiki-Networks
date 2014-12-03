import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
from collections import defaultdict
import yaml

'''Given a start and end date, return the distribution of collaborators
for each page.
A collaborator has to have edited both before and after >=1 other user.'''

with open('./config.yaml', 'rb') as f:
    config = yaml.load(f)
startDate = config['startDate']
endDate = config['endDate']
userTalkCats = config['userTalkCats']
contentTalkCats = config['contentTalkCats']
globalTalkCats = config['globalCats']
allTalk = userTalkCats + contentTalkCats + globalTalkCats
# If selectedCats is blank, then talk is removed. Otherwise, only pages
# in the selected categories are analyzed
selectedCats = ['Person','Family']

conn = psycopg2.connect("dbname={} user={}".format(config['database'], config['user']))

def getNonTalkPageList():
    '''Gets a list of pages which are not in the ignoredCats list.'''
    cur = conn.cursor()
    cur.execute("""SELECT page_id from pages
            WHERE page_category IN %s
            ORDER BY page_id ASC;""", (tuple(selectedCats),))
    pages = cur.fetchall()
    pages = [x[0] for x in pages]
    return pages

def getCollaboratorCount(pageID):
    editors = getEditorsFromPage(pageID)
    collaborators = getCollaboratorsFromEditors(editors)
    return len(collaborators)

def getEditorsFromPage(page):
    edits = getPageEdits(page, startDate, endDate)
    editors = [x[0] for x in edits]
    return editors

def getCollaboratorsFromEditors(editorList):
    collaborators = []
    for i, editor in enumerate(editorList):
        if editor not in collaborators:
            # Get the index of their next edit. If it's not the next edit,
            # that means someone else edited in between, and the editor
            # qualifies as a collaborator.
            try:
                nextEdit = editorList[i+1:].index(editor)
                if nextEdit > 0:
                    collaborators.append(editor)
            # If the editor didn't edit again, then they don't qualify
            except:
                continue
    return collaborators

def getPageEdits(pageID, startTime, endTime):
    '''Takes a page ID, returns all of the edits that occurred between the start time and end time'''
    cur = conn.cursor()
    cur.execute("""SELECT user_id, edit_time, comment from temp_edits WHERE page_id = %s
            AND edit_time > %s AND edit_time < %s
            ORDER BY edit_time DESC;""", (pageID, startTime, endTime))
    edits = cur.fetchall()
    return edits



def main():
    collaboratorCount = {}
    pages = getNonTalkPageList()
    i = 0
    maxContribs = [(0,0)]
    for page in pages:
        i += 1
        if i % 10000 == 0:
            print 'Page {}; ID: {}'.format(i,page)
            print 'Current Count: {}'.format(collaboratorCount)
        currCollabCount = getCollaboratorCount(page)
        if currCollabCount in collaboratorCount:
            collaboratorCount[currCollabCount] += 1
        else:
            collaboratorCount[currCollabCount] = 1
            if currCollabCount > maxContribs[-1][0]:
                maxContribs.append((currCollabCount, page))
    result = sorted([(k,v) for k,v in collaboratorCount.iteritems()])
    print result
    print maxContribs

if __name__ == '__main__':
    main()
