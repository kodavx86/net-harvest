# Network module used by net-harvest
#
# Author: kodavx86
# Created: 02.19.2018

import os, socket, subprocess, shlex
import tempfile, xml.etree.ElementTree as ET
import requests, defaults

def ping(address):
    # Ping the given address
    r = os.system("/bin/ping -c {} -W {} ".format(defaults.PING_RETRY,
                                                  defaults.PING_TIMEOUT) + address);

    if 0 == r:
        return True;
    return False;

def tcp(address, port):
    # Make TCP connection to the address/port
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
    try:
        s.settimeout(defaults.TCP_TIMEOUT);
        s.connect((address, port));
        s.close();
    except Exception:
        return False;
    return True;

def ssh_probe(address, port):
    # Probe the endpoint for the SSH version
    cmd = '/usr/bin/ssh-keyscan -p {} {}'.format(port, address);
    proc = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.STDOUT);
    out,err = proc.communicate();

    return str(out);

def http_probe(address, port, https=False):
    # Probe the endpoint for the http service
    try:
        if not https:
            r = requests.get('http://{}:{}'.format(address, port));
        else:
            r = requests.get('https://{}:{}'.format(address, port), verify=False);
    except Exception:
        return '';
    hlist = list(r.headers.keys());
    hlist.sort();
    out = '';
    for k in hlist:
        out += '{}: {}\n'.format(k, r.headers[k]);
    return out;

def nmap_prob(address, port):
    # Use nmap to probe the endpoint
    fp = tempfile.NamedTemporaryFile(dir='/tmp/');
    cmd = '/usr/bin/nmap -p {} -oX {} --open -sV {}'.format(
        port, fp.name, address);
    os.system(cmd);
    with open(fp.name, 'r') as f:
        data = f.read();
    r_tree = ET.ElementTree(ET.fromstring(data));
    for elem in r_tree.iter(tag='service'):
        service = elem.get('name','unknown');
        version = elem.get('version','unknown');
    fp.close();
    return (service, version);

def probe(service, address, port):
    service_probe = {
        'ssh' : ssh_probe,
        'http' : http_probe,
        'https' : http_probe
    };

    if service.lower() in service_probe:
        return service_probe[service.lower()](address, port);
    return None;

