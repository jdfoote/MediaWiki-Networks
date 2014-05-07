\copy
(SELECT userstats.*, 
		(userstats.end_date - users.first_edit) AS daysSinceFirstEdit 
		FROM userstats INNER JOIN users 
		ON userstats.user_id = users.user_id 
		WHERE userstats.end_date >= users.first_edit 
		AND users.is_bot = FALSE
		AND userstats.all_edits > 5) 
TO '/home/jeremy/Desktop/userStats.csv' 
DELIMITER ',' CSV HEADER;
