# Database interface for net-harvest
#
# Author: kodavx86
# Created: 02.19.2018

import sqlite3, time, json

# Globals
DATABASE = '/home/net-harvest/database/db.sqlite'

def create_job():
    # Connect to the database
    conn = sqlite3.connect(DATABASE);
    cursor = conn.cursor();

    # Insert new job row
    data = (int(time.time()),'waiting');
    cursor.execute("INSERT INTO Jobs (start_time,status) VALUES(?,?)", data);
    rowid = cursor.lastrowid;

    # Commit the new job
    conn.commit();

    # Close the database connection
    conn.close();

    # Return the new job id
    return rowid;

def update_job(job_id, status, end_time=None):
    # Connect to the database
    conn = sqlite3.connect(DATABASE);
    cursor = conn.cursor();

    # Update the job status
    if end_time is None:
        data = (status, job_id);
        cursor.execute("UPDATE Jobs SET status = ? WHERE ID = ?", data);
    else:
        data = (status, end_time, job_id);
        cursor.execute("UPDATE Jobs SET status = ?, end_time = ? WHERE ID = ?", data);

    # Commit the new job
    conn.commit();

    # Close the database connection
    conn.close();

    return True;

def add_ping_result(job_id, address):
    # Connect to the database
    conn = sqlite3.connect(DATABASE);
    cursor = conn.cursor();

    # Insert new icmp row
    data = (job_id, address, 'icmp');
    cursor.execute(
        "INSERT INTO Network (job_id,ip_address,protocol) VALUES(?,?,?)", data);

    # Commit the new icmp data
    conn.commit();

    # Close the database connection
    conn.close();

    return;

def add_tcp_result(job_id, address, port, service, data=None):
    # Connect to the database
    conn = sqlite3.connect(DATABASE);
    cursor = conn.cursor();

    # Insert new tcp row
    if data is not None:
        params = (job_id, address, 'tcp', port, service, data);
        cursor.execute(
            "INSERT INTO Network (job_id,ip_address,protocol," \
            "port,service,data) VALUES(?,?,?,?,?,?)", params);
    else:
        params = (job_id, address, 'tcp', port, service);
        cursor.execute(
            "INSERT INTO Network (job_id,ip_address,protocol," \
            "port,service) VALUES(?,?,?,?,?)", params);

    # Commit the new tcp data
    conn.commit();

    # Close the database connection
    conn.close();

    return;

def get_job_data(job_id):
    # Connect to the database
    conn = sqlite3.connect(DATABASE);
    conn.row_factory = sqlite3.Row;
    cursor = conn.cursor();

    # Get the job data
    params = (job_id,);
    cursor.execute("SELECT status, ip_address, protocol, port, service, data" \
                   " from Jobs LEFT OUTER JOIN Network on Jobs.id = Network.job_id" \
                   " where Jobs.id = ?", params);

    # Prepare the data
    j_data = {'status' : None, 'discover' : {}};
    for row in cursor:
        j_data['status'] = row['status'];
        if row['ip_address'] in j_data['discover'].keys():
            j_data['discover'][row['ip_address']].append(
                {
                    'protocol' : row['protocol'],
                    'port' : row['port'],
                    'service' : row['service'],
                    'data' : row['data']
                }
            );
        else:
            j_data['discover'][row['ip_address']] = [
                {
                    'protocol' : row['protocol'],
                    'port' : row['port'],
                    'service' : row['service'],
                    'data' : row['data']
                }
            ];

    # Close the database connection
    conn.close();

    return json.dumps(j_data);

def delete_job(job_id):
    # Connect to the database
    conn = sqlite3.connect(DATABASE);
    cursor = conn.cursor();

    # Delete the job with job_id
    params = (job_id,);
    cursor.execute("DELETE FROM Jobs WHERE id = ?", params);

    # Commit the job deletion
    conn.commit();

    # Close the database connection
    conn.close();

    return;

def get_all_jobs_summary():
    # Connect to the database
    conn = sqlite3.connect(DATABASE);
    conn.row_factory = sqlite3.Row;
    cursor = conn.cursor();

    # Get the job data
    cursor.execute("SELECT id, start_time, end_time, status from Jobs");
    j_data = [];
    for row in cursor:
        r_data = {};
        r_data['id'] = row['id'];
        r_data['start_time'] = row['start_time'];
        r_data['end_time'] = row['end_time'];
        r_data['status'] = row['status'];
        j_data.append(r_data);

    # Close the database connection
    conn.close();

    return j_data;

