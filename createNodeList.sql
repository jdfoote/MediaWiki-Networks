\copy (SELECT DISTINCT(users.user_id) 
		FROM userstats, users 
		WHERE userstats.user_id = users.user_id 
		AND manual_edits_total >5 
		AND start_date > '2012-06-01' 
		AND users.first_edit < '2012-06-03') TO '/home/jeremy/Programming/WeRelate/DataFiles/overFiveEditsStartBefore20120603.csv' WITH CSV;
