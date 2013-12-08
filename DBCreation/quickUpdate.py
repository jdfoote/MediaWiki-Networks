import psycopg2
import datetime as dT
import yaml
import sys
sys.path.append("../")
import networkTools as nT
import csv

resultsFile = './activeDays.csv'
conn = psycopg2.connect("dbname=weRelate user=jeremy")

with open('config.yaml', 'r') as f:
    config = yaml.load(f)

startDate = config['startDate']
endDate = config['endDate']
delta = config['timeDelta']


users = nT.getActiveUsers(startDate, endDate)

print "starting inserting"
with open(resultsFile, 'rb') as f:
    i = csv.reader(f)
    for row in i:
        user, currStart, allEdits, days = row
        print user
        cur = conn.cursor()
        cur.execute("""UPDATE userstats SET active_days = %s, all_edits = %s WHERE user_id = %s AND start_date = %s""", (days, allEdits, user, currStart))
        cur.close()
        conn.commit()
