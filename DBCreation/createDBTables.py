import psycopg2
import datetime as dT

def getPages():
    '''Gets all of the pages from the DB, and creates a list of dictionaries,
    and inserts them into the pages table'''
    cur = conn.cursor(name='pages')
    cur.execute("SELECT DISTINCT page_id, page_name, page_category FROM edits")
    # Get the first 1000
    currResults = cur.fetchmany(1000)
    # Keep going while there are results
    index = 1
    while currResults:
        pageList = []
        for page in currResults:
            pageList.append({'page_id':page[0], 'page_name':page[1], 'page_category':page[2]})
        print "Inserting pages {} to {}".format(index, index+999)
        createPages(pageList)
        currResults = cur.fetchmany(1000)
        index += 1000
    conn.commit()

def createPages(pageDict):
    cur = conn.cursor()
    cur.executemany("INSERT INTO pages(page_id, page_name, page_category) VALUES (%(page_id)s, %(page_name)s, %(page_category)s);", pageDict)
    cur.close()

def getUsers():
    '''Gets all of the users from the DB, and creates a list of dictionaries, ready to be inserted'''
    cur = conn.cursor(name='pages')
    cur.execute("""SELECT DISTINCT ON (user_id) user_id, user_name FROM edits
            ORDER BY user_id, edit_time DESC;""")
    # Get the first 1000
    currResults = cur.fetchmany(1000)
    # Keep going while there are resultsi
    index = 1
    while currResults:
        userList = []
        print "Inserting pages {} to {}".format(index, index+999)
        for user in currResults:
            user_id = user[0]
            if not user_id:
                user_id = 0
            userList.append({'user_id':user_id, 'user_name':user[1]})
        createUsers(userList)
        currResults = cur.fetchmany(1000)
        index += 1000
    conn.commit()

def createUsers(userDict):
    cur = conn.cursor()
    cur.executemany("INSERT INTO users(user_id, user_name) VALUES (%(user_id)s, %(user_name)s);", userDict)
    cur.close()

if __name__ == '__main__':
    print "Connecting to DB..."
    conn = psycopg2.connect("dbname=weRelate user=jeremy")
    print "Getting pages..."
    #getPages()
    print "Getting users..."
    getUsers()
