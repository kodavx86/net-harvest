# Flask API interface for net-harvest
#
# Author: kodavx86
# Created: 02.19.2018

from flask import Flask, Response, request, render_template
import json, multiprocessing, datetime
import db, worker
from dateutil import tz

app = Flask(__name__)

@app.route('/net-harvest/api/v1/alive', methods=['GET'])
def alive():
 return Response(status=200);

@app.route('/net-harvest/api/v1/scan', methods=['POST'])
def scan():
 try:
  data = request.get_json();
 except Exception as e:
  return Response(json.dumps({"summary" : "Failed to extract parameters"}),
                  status=400, mimetype='application/json');

 # Extract paramters
 if 'ip_range' not in data:
  return Response(json.dumps({"summary" : "Missing IP range"}),
                  status=400, mimetype='application/json');
 if 'start' not in data['ip_range'] or 'end' not in data['ip_range']:
  return Response(json.dumps({"summary" : "Missing IP range start/end"}),
                  status=400, mimetype='application/json');
 ip_start = data['ip_range']['start'];
 ip_end = data['ip_range']['end'];
 exc_ip_start = None;
 exc_ip_end = None;

 if 'exclude_ips' in data:
  if 'start' not in data['exclude_ips'] or 'end' not in data['exclude_ips']:
   return Response(json.dumps({"summary" : "Missing exclude IP start/end"}),
                   status=400, mimetype='application/json');
  exc_ip_start = data['exclude_ips']['start'];
  exc_ip_end = data['exclude_ips']['end'];

 if 'protocol' not in data:
  return Response(json.dumps({"summary" : "Missing protocol list"}),
                  status=400, mimetype='application/json');
 protocols = data['protocol'];

 if 'port' not in data:
  return Response(json.dumps({"summary" : "Missing port list"}),
                  status=400, mimetype='application/json');
 ports = data['port'];

 # Create a new database job entry
 job_id = db.create_job();
 data['job_id'] = job_id;

 # Spawn a worker process
 w = multiprocessing.Process(target=worker.spawn_worker, args=(data,));
 w.daemon = True;
 w.start();

 return Response(json.dumps({"job_id" : job_id}), status=200,
                 mimetype='application/json');

@app.route('/net-harvest/api/v1/job/<jobid>', methods=['GET'])
def get_job(jobid):
 return Response(db.get_job_data(jobid), status=200, mimetype='application/json');

@app.route('/net-harvest/api/v1/job/<jobid>', methods=['DELETE'])
def purge_job(jobid):
 # Check if the job is running or not
 j_data = json.loads(db.get_job_data(jobid));
 if 'finished' != j_data['status']:
  return Response(json.dumps({"message" : "Job not finished or does not exist. Cannot delete"}),
                  status=400, mimetype='application/json');
 db.delete_job(jobid);
 return Response(json.dumps({"message" : "Job deleted"}), status=200,
                 mimetype='application/json');

@app.route('/', methods=['GET'])
def homepage():
 # Get all job summary data from db
 j_data = db.get_all_jobs_summary();

 # Convert job times to local times
 ftz = tz.gettz('UTC');
 ttz = tz.tzlocal();
 for j in j_data:
  start_time = j['start_time'];
  utc_sdate = datetime.datetime.fromtimestamp(start_time);
  utc_sdate = utc_sdate.replace(tzinfo=ftz);
  local_sdate = utc_sdate.astimezone(ttz);
  j['start_time'] = str(local_sdate);

  if 0 == j['end_time']:
   j['end_time'] = '--';
  else:
   end_time = j['end_time'];
   utc_edate = datetime.datetime.fromtimestamp(end_time);
   utc_edate = utc_edate.replace(tzinfo=ftz);
   local_edate = utc_edate.astimezone(ttz);
   j['end_time'] = str(local_edate);

 # Prepare the template parameters
 r_params = {'title' : 'Summary', 'j_data' : j_data};

 return render_template('summary.html', r_params=r_params);

if __name__ == '__main__':
 # This is executed when net-harvest is run locally
 app.run(debug=True, host='0.0.0.0')

