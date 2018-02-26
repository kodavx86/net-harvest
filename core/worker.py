# Worker module for net-harvest
#
# Author: kodavx86
# Created: 02.19.2018

import time, os
from ipaddress import ip_address
import xml.etree.ElementTree as ET
import network, db

def spawn_worker(data):
    # Update job status to running
    db.update_job(data['job_id'], 'running');

    # Get list of all target IPs
    start = ip_address(data['ip_range']['start']);
    end = ip_address(data['ip_range']['end']);
    targets = [];
    while start <= end:
        targets.append(str(start));
        start += 1;
    exclude = [];
    if 'exclude_ips' in data:
        exc_start = ip_address(data['exclude_ips']['start']);
        exc_end = ip_address(data['exclude_ips']['end']);
        while exc_start <= exc_end:
            exclude.append(str(exc_start));
            exc_start += 1;
    targets = [t for t in targets if t not in exclude];

    # Create a job directory
    os.mkdir('/var/tmp/jobs/{}'.format(data['job_id']));
    data['job_dir'] = '/var/tmp/jobs/{}'.format(data['job_id']);

    # Conduct ICMP scan
    if 'icmp' in data['protocol']:
        icmp_scan(data, targets);

    # Conduct TCP scan
    if 'tcp' in data['protocol']:
        tcp_scan(data, targets);

    # Update job status to finished
    db.update_job(data['job_id'], 'finished', int(time.time()));

    return;

def icmp_scan(data, targets):
    # Ping the targets in the list
    for t in targets:
        if network.ping(t):
            db.add_ping_result(data['job_id'], t);

def tcp_scan(data, targets):
    # Use TCP to connect to targets in the list
    for t in targets:
        for p in data['port']:
            if network.tcp(t,p):
                # Use nmap to identify service
                of = data['job_dir'] + '/tcp_nmap.xml';
                cmd = '/usr/bin/nmap -p {} -oX {} --open {}'.format(p, of, t);
                os.system(cmd);
                with open(of, 'r') as f:
                    output = f.read();
                r_tree = ET.ElementTree(ET.fromstring(output));
                service = '';
                for elem in r_tree.iter(tag='service'):
                    service = elem.get('name','unknown');

                # Probe the service
                response = network.probe(service, t, p);

                # Recored the results in the database
                db.add_tcp_result(data['job_id'], t, p, service, response);
    return;

