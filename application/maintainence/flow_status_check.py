import sys
import requests
import json
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway

nifi_api_url = sys.argv[1]
prometheus_pushgateway_url = sys.argv[2]
artifact_id = sys.argv[3]

flow_file_loc = nifi_api_url + '/flow/status'
alert_name = artifact_id + 'FlowfileMetric'


def flow_files_queue():
    r = requests.get(flow_file_loc, allow_redirects=True)
    a = (json.dumps(r.json(), indent=2))
    resp = json.loads(a)
    return resp['controllerStatus']['flowFilesQueued']


registry = CollectorRegistry()
g = Gauge(alert_name, 'Last Unix time when change was pushed', registry=registry)
g.set_to_current_time()
g.set(flow_files_queue())
push_to_gateway(prometheus_pushgateway_url, job=alert_name, registry=registry)
