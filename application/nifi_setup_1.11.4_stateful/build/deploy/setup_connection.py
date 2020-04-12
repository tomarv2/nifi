import os
import logging
logger = logging.getLogger(__name__)
FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(format=FORMAT, level=os.environ.get("LOGLEVEL", "DEBUG"))
dict_for_communication = {}
temp_file = '/tmp/setup_connection.txt'

# parse_connections = 1
# parse_sourceId = '"Dash_DeltaID_company"'
# parse_sourceGroupId = '"Dash_Company_DeltaID"'
# parse_destinationId = '"RemoteInputPort_company"'
# parse_destinationGroupId = '"/remote-process-groups/'
# nifi_api_url = 'http://nifi.demo.com/nifi-api'


def get_dict_for_comm(parse_connections,
                      parse_sourceId,
                      parse_sourceGroupId,
                      parse_destinationId,
                      parse_destinationGroupId,
                      nifi_api_url):
    logger.debug("list passed to get_dict_for_comm: \n"
                 "number of connections to make: %s\n"
                 "sourceId: %s\n"
                 "destinationId: %s\n"
                 "destinationGroupId (remote process group name): %s\n"
                 "nifi url: %s", parse_connections,
                                 parse_sourceId,
                                 parse_sourceGroupId,
                                 parse_destinationId,
                                 parse_destinationGroupId,
                                 nifi_api_url)
    temp_location = "curl -XGET %s/resources | jq . > %s" % (nifi_api_url, temp_file)
    logger.debug("temp location: %s", temp_location)
    os.system(temp_location)
    #raise SystemExit
    previous_line = ""
    try:
        f = open(temp_file, 'r')
    except:
        logger.debug("unable to open file: %s", temp_file)
        raise SystemExit
    try:
        for current_line in f:
            if parse_sourceId in current_line:
                if parse_sourceId in current_line:
                    sourceId = previous_line.split('/')[-1].split('"')[0]
                    #dict_for_communication.append("sourceId")
                    sourceId_update = {"sourceId": sourceId}
                    dict_for_communication.update(sourceId_update)

            if parse_sourceGroupId in current_line:
                if parse_sourceGroupId in current_line:
                    sourceGroupId = previous_line.split('/')[-1].split('"')[0]
                    #dict_for_communication.append("sourceGroupId")
                    sourceGroupId_update = {"sourceGroupId": sourceGroupId}
                    dict_for_communication.update(sourceGroupId_update)

            if parse_destinationId in current_line:
                if parse_destinationId in current_line:
                    destination_Id = previous_line.split('/')[-1].split('"')[0]
                    #dict_for_communication.append("destination_Id")
                    destination_Id_update = {"destinationId": destination_Id}
                    logger.debug("destinationId_update: %s", destination_Id_update)
                    dict_for_communication.update(destination_Id_update)

            if parse_destinationGroupId in current_line:
                #if parse_destinationGroupId in current_line:
                remote_process = current_line.split('/')[-1].split('"')[0]
                #dict_for_communication.append("remote_process")
                remote_process_update = {"destinationGroupId": remote_process}
                logger.debug("parse_destinationGroupId: %s", remote_process_update)
                dict_for_communication.update(remote_process_update)
            previous_line = current_line
    except:
        logger.debug("unable to parse file for setting up link...")
        raise SystemExit
    #logger.debug("dict returned from setting up communication: %s", dict_for_communication)
    return dict_for_communication

# print(get_dict_for_comm(parse_connections,
#                       parse_sourceId,
#                       parse_sourceGroupId,
#                       parse_destinationId,
#                       parse_destinationGroupId,
#                       nifi_api_url))
#
# # for k in dict_for_communication:
# #     logger.debug("key:", k)
# for key, value in dict_for_communication.items():
#     print(value)
