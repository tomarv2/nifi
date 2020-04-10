import os
import logging
logger = logging.getLogger(__name__)
FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(format=FORMAT, level=os.environ.get("LOGLEVEL", "DEBUG"))
controller_services = []
temp_file = '/tmp/setup_controller_services.txt'


def controller_services_list(nifi_api_url):
    temp_location = 'curl -XGET %s/resources | jq . | grep -i \\"/controller-services/ > %s' % (nifi_api_url, temp_file)
    os.system(temp_location)
    f = open(temp_file, 'r')
    for line in f:
        controller_services.append(line.split('/')[-1].split('"')[0])
    return controller_services

