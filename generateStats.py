import psycopg2
import datetime as dt
import csv

ignoreList = ('0','48')
conn = psycopg2.connect("dbname=weRelate user=jeremy")


def getOverallStats(startDate, endDate, delta):
    '''Takes a start date and endDate as datetimes, and returns a summary of each delta-length
    period between dates (where delta is number of days). The final period may be truncated.'''
    stats = []
    cur = conn.cursor()

    while startDate < endDate:
        curEndDate = startDate + dt.timedelta(days=delta)
        cur.execute("SELECT count(*) from temp_edits WHERE user_id NOT IN %s AND edit_time > %s AND edit_time < %s AND is_propagation = %s AND comment != %s",
                (ignoreList, startDate, curEndDate, False, 'gedcom upload'))
        count = cur.fetchone()[0]
        stats.append((startDate, curEndDate, count))
        startDate = curEndDate
    cur.close()
    return stats

def getUserEditSummary(user, delta, startDate=dt.datetime(2000,1,1), endDate=dt.datetime.now()):
    '''Takes a start date, end date (both datetimes), user id, and delta (in days). Returns a
    summary of the number of edits for each delta-length period between dates for that user.'''
    stats = [user]
    cur = conn.cursor()
    cur.execute("SELECT edit_time from temp_edits WHERE user_id = %s AND edit_time > %s AND edit_time < %s AND is_propagation = %s AND is_gedcom = %s ORDER BY edit_time ASC",
            (user, startDate, endDate, False, False))
    allEdits = cur.fetchall()
    while startDate < endDate:
        curEndDate = startDate + dt.timedelta(days=delta)
        currTotal = sum(x[0] > startDate and x[0] < curEndDate for x in allEdits)
        stats.append(currTotal)
        startDate = curEndDate
    cur.close()
    return stats

def getUsers(startDate=dt.datetime(2000,1,1), endDate=dt.datetime.now(), pageCategory='', allUsers=False):
    '''Takes a list of categories that editors must have edited in order to be included.
    Returns a list of user ids, and their first edit date.
    The allUsers parameter is because I'm lazy. If it's true, then it ignores the other params,
    and just returns all of the users.
    '''
    cur = conn.cursor()
    # Get subset of users, based on edits
    if not allUsers:
        cur.execute("SELECT DISTINCT user_id, first_edit, last_edit FROM non_bot_edits WHERE edit_time > %s AND edit_time < %s AND page_category = %s",
            (startDate, endDate, pageCategory))
    # Otherwise, get all users
    else:
        cur.execute("SELECT user_id, first_edit, last_edit FROM users where is_bot = %s", (False,))

    return cur.fetchall()

def getUserStatsByFirstEdit(): if __name__ == '__main__':
    delta = 7
    allUsers = True
    with open('userStatsByFirstEdit.csv', 'wb') as o:
        output = csv.writer(o)
        print 'Getting users'
        users = getUsers(allUsers = allUsers)
        print 'Writing results'
        i = 0
        for user in users:
            # Convert start date to datetime
            startDate = dt.datetime.combine(user[1], dt.time(0,0))
            endDate = dt.datetime.combine(user[2], dt.time(23,59))
            userStats = getUserEditSummary(user = user[0], startDate = startDate, endDate = endDate, delta = delta)
            output.writerow(userStats)
            if i % 100 == 0:
                print 'User {}'.format(i)
            i += 1

