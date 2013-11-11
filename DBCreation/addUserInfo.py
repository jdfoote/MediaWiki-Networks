import psycopg2
import datetime as dT

botList = [0,1,2,48,'0','1','2','48']
editCats = {'Family':'family_edits','Family talk': 'family_talk_edits','Person': 'person_edits',
        'Person talk': 'person_talk_edits', 'Place': 'place_edits',
        'Place talk': 'place_talk_edits', 'Article': 'other_edits', 'Category':'organizing_edits',
        'Category talk': 'organizing_talk_edits', 'Givenname':'organizing_edits',
        'Givenname talk':'organizing_talk_edits', 'Help': 'community_related_edits',
        'Help talk': 'community_related_talk_edits','Image':'source_related_edits',
        'Image talk': 'source_related_talk_edits', 'MediaWiki': 'other_edits',
        'MediaWiki talk':'other_edits', 'MySource':'source_related_edits',
        'MySource talk':'source_related_talk_edits','Portal':'organizing_edits',
        'Portal talk':'organizing_talk_edits','Repository':'source_related_edits',
        'Repository talk':'source_related_talk_edits', 'Source': 'source_related_edits',
        'Source talk':'source_related_talk_edits', 'Surname': 'organizing_edits',
        'Surname talk': 'organizing_talk_edits', 'Talk':'other_edits',
        'Template':'organizing_edits', 'Template talk':'organizing_talk_edits',
        'Transcript': 'source_related_edits','User': 'user_page_edits',
        'User talk': 'user_page_talk_edits', 'WeRelate': 'community_related_edits',
        'WeRelate talk': 'community_related_talk_edits'}

def getAndUpdateUsers():
    '''Gets all of the users from the DB, and creates a list of dictionaries,
    and then inserts them into the DB'''
    cur = conn.cursor(name='pages')
    cur.execute("""SELECT user_id FROM users
            ORDER BY user_id;""")
    # Get the first 1000
    currResults = cur.fetchmany(1000)
    # Keep going while there are results
    index = 1
    while currResults:
        userList = []
        print "Inserting users {} to {}".format(index, index+999)
        for user in currResults:
            user_id = user[0]
            if user_id not in botList:
                userStats = getUserStats(user_id)
                userList.append(userStats)
        updateUsers(userList)
        currResults = cur.fetchmany(1000)
        index += 1000
    conn.commit()

def getUserStats(user):
    '''Takes a user Id, and returns a dictionary with their stats for each category type'''
    cur = conn.cursor()
    cur.execute("""SELECT page_category from non_bot_edits
            WHERE user_id = %s;""", (user,))
    edits = cur.fetchall()
    userStats = {k:0 for k in editCats.values()}
    userStats['manual_edit_count'] = len(edits)
    userStats['user_id'] = user
    for e in edits:
        catType = editCats[e[0]]
        userStats[catType] += 1
    return userStats

def updateUsers(userList):
    '''Takes a list of user dictionaries, and updates the DB for all of them, based
    on the entries in the dictionary'''
    cur = conn.cursor()
    query = "UPDATE users SET "
    for k in userList[0]:
        if k != 'user_id':
            query += "{} = %({})s, ".format(k, k)
    query = query[:-2] + 'WHERE user_id = %(user_id)s;'
    cur.executemany(query,
    userList)
    cur.close()

if __name__ == '__main__':
    print "Connecting to DB..."
    conn = psycopg2.connect("dbname=weRelate user=jeremy")
    print "Getting users..."
    getAndUpdateUsers()
