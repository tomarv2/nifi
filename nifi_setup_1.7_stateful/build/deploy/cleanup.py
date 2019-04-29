import requests
import time
import sys
import subprocess

node_list_url = sys.argv[1]+'/nifi-api/controller/cluster'
delete_node_url = sys.argv[1]+'/nifi-api/controller/cluster/nodes'


def check():
    try:
        r = requests.get(node_list_url,timeout=3)
        r.raise_for_status()
        return 1
    except requests.exceptions.HTTPError as errh:
        print ("Http Error:",errh)
    except requests.exceptions.ConnectionError as errc:
        print ("Error Connecting:",errc)
    except requests.exceptions.Timeout as errt:
        print ("Timeout Error:",errt)
    except requests.exceptions.RequestException as err:
        print ("OOps: Something Else",err)


def delete_node(node_id):
    time.sleep(5)
    cmd_to_delete = 'curl -XDELETE %s/%s' % (delete_node_url, node_id)
    #print "delete cmd: ", cmd_to_delete
    proc = subprocess.Popen(cmd_to_delete, stdout=subprocess.PIPE, shell=True)
    proc.communicate()

while check() != 1:
    print ("waiting for cluster to be reachable...")
    time.sleep(10)
else:
    time.sleep(5)
    print ("getting list of nodes...")
    list_cmd = 'curl -XGET %s | jq \'.\' | grep \'\"nodeId\' | awk \'{print $2}\'| cut -f2 -d \'"\'' % node_list_url
    #print list_cmd
    proc = subprocess.Popen(list_cmd, stdout=subprocess.PIPE, shell=True)
    (template_id, err) = proc.communicate()
    for node_id_value in template_id.split('\n'):
        print ("node id:", node_id_value)
        delete_node(node_id_value)
