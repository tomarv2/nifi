from prometheus_client import start_http_server, Summary
import random
import time
import os
import subprocess

def test():
    a = []
    list_all_processor_groups = 'find /mnt/nifi/oneanddone -name "*.txt" -mmin -1'
    proc = subprocess.Popen(list_all_processor_groups, stdout=subprocess.PIPE, shell=True)
    (root_proc_grp, err) = proc.communicate()
    a.append(root_proc_grp)
    for line in a:
        byte_s = line.decode()
        if 'test_nifi_template_status.txt' in (byte_s):
            return ("pass")
# Create a metric to track time spent and requests made.
REQUEST_TIME = Summary('request_processing_seconds', 'Time spent processing request')

# Decorate function with metric.
@REQUEST_TIME.time()
def process_request(t):
    print ("metric")
    """A dummy function that takes some time."""
    time.sleep(t)

if __name__ == '__main__':
    # Start up the server to expose the metrics.
    start_http_server(9172)
    # Generate some requests.
    while True:
        try:
            print (test())
            if 'pass' in (test()):
                process_request(random.random())
        except:
            pass