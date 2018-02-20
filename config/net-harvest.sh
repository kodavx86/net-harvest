#!/usr/bin/env bash
set -e

# Create the database
sqlite3 /home/net-harvest/database/db.sqlite "CREATE TABLE Jobs(\
id INTEGER PRIMARY KEY AUTOINCREMENT, start_time INT NOT NULL,\
end_time INT DEFAULT 0, status TEXT NOT NULL);"

sqlite3 /home/net-harvest/database/db.sqlite "CREATE TABLE Network(\
id INTEGER PRIMARY KEY AUTOINCREMENT, job_id INT, ip_address TEXT NOT NULL,\
protocol TEXT NOT NULL, port INT DEFAULT NULL, service TEXT DEFAULT NULL,\
data TEXT DEFAULT NULL, Foreign KEY(job_id) REFERENCES Jobs(id) ON DELETE CASCADE);"

# Create a jobs directory
mkdir /var/tmp/jobs/

# Start the net-harvest server
echo "Running the net-harvest server..."
exec uwsgi --http-socket 0.0.0.0:8181 --wsgi-file /opt/net-harvest/core/server.py \
     --callable app --master --processes 5 --http-timeout 300 --pidfile /tmp/app.pid

