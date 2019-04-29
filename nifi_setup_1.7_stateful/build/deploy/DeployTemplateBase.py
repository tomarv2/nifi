import logging
logger = logging.getLogger(__name__)
import os
import requests
import json
import subprocess
import copy


class DeployTemplate:
    def __init__(self, nifi_api_url):
        self.nifi_api_url = nifi_api_url
        self.url = self.nifi_api_url + '/flow/process-groups/root'
        self.template_id = []
        self.child_proc_grp_list = []
        self.final_proc_grp_list = []
        self.remote_process_groups = []
        self.list_ctrl_services = []
        self.remote_process_group_list = []
        self.output_ports_list = []
        self.get_output_port_list = []
        self.list_input_host_port_list = []
        self.get_host_port_version = {}
        self.controller_services_version = {}
        self.process_groups_version = {}
        self.final_list_of_processes = []
        self.component_id_list = []
        self.get_host_port_type = []
        self.get_RouteOnAttribute_port_id_list = []

    def flatten(self, S):
        if S == []:
            return S
        if isinstance(S[0], list):
            return self.flatten(S[0]) + self.flatten(S[1:])
        return S[:1] + self.flatten(S[1:])

    def root_process_grp(self):
        r = requests.get(self.url, allow_redirects=True)
        a = (json.dumps(r.json(), indent=2))
        resp = json.loads(a)
        del self.final_list_of_processes[:]
        self.final_list_of_processes.append(resp['processGroupFlow']['breadcrumb']['breadcrumb']['id'])
        return resp['processGroupFlow']['breadcrumb']['breadcrumb']['id']

    def validate_template(self):
        upload_template_url = "curl -XGET %s/flow/templates | jq '.' | grep id" % self.nifi_api_url
        validate_template_existance = subprocess.call(upload_template_url, shell=True)
        if not validate_template_existance:
            logger.info("\ntemplate already exists...\n")
            raise SystemExit

    def upload_template(self, file_to_upload, download_dir):
        self.file_to_upload = file_to_upload
        upload_template_url = 'curl --connect-timeout 30 -i -F template=@%s/templates/%s -X POST %s/process-groups/%s/templates/upload' \
        % (download_dir, self.file_to_upload, self.nifi_api_url, self.root_process_grp())
        logger.info("upload template command: \n%s", upload_template_url)
        os.system(upload_template_url)

    def get_template_id(self):
        a = "curl -s -X GET %s/resources | jq '.' | grep '\"/templates/' | awk '{print $2}' | sed 's/\\\"//g'| \
        sed 's/\/templates\///g' | sed 's/\,//g'" % (self.nifi_api_url)
        proc = subprocess.Popen(a, stdout=subprocess.PIPE, shell=True)
        (template_id, err) = proc.communicate()
        self.template_id.append(template_id)

    def instantiate_template(self, template_all):
        coordinate_y = 0.0
        for template in template_all:
            instantiate_temp = 'curl --connect-timeout 10 -H "Content-Type: application/json" -X POST -d \'{"originX": 10.0, \
            "originY": %s, "templateId": "%s"}\' %s/process-groups/%s/template-instance' % (coordinate_y, template, self.nifi_api_url, self.root_process_grp().strip())
            logger.debug("instantiating command: %s", instantiate_temp)
            proc = subprocess.Popen(instantiate_temp, stdout=subprocess.PIPE, shell=True)
            proc.communicate()
            logger.info("instantiating: \n%s", instantiate_temp)
            coordinate_y = coordinate_y + 800

    def process_grp_under_root(self, root_process):
        list_all_processor_groups = 'curl -s -X GET %s/process-groups/%s/process-groups| jq \'.\' | grep \'\"id\"\'|\
        awk \'{print $2}\'|uniq|sed \'s/\,//g\'|sed \'s/\\\"//g\'' % (self.nifi_api_url, root_process)
        proc = subprocess.Popen(list_all_processor_groups, stdout=subprocess.PIPE, shell=True)
        (root_proc_grp, err) = proc.communicate()
        self.final_list_of_processes.append(root_proc_grp.strip())
        return root_proc_grp.strip()

    # list process groups
    def list_processor_grp(self, process_id):
        for item in process_id:
            child_processor_groups = 'curl -s -X GET %s/process-groups/%s/process-groups| jq \'.\' | grep \'\"id\"\'|\
            awk \'{print $2}\'|uniq|sed \'s/\,//g\'|sed \'s/\\\"//g\'' % (self.nifi_api_url, item)
            proc = subprocess.Popen(child_processor_groups, stdout=subprocess.PIPE, shell=True)
            (child, err) = proc.communicate()
            self.child_proc_grp_list.append(child.splitlines())
            self.final_proc_grp_list.append(child.splitlines())
            self.final_list_of_processes.append(child.splitlines())

    def check_list(self):
        try:
            if not len(self.child_proc_grp_list[0]) == 0:
                new_list = copy.copy(self.child_proc_grp_list)
                del self.child_proc_grp_list[:]
                for x in new_list:
                    self.list_processor_grp(x)
                self.check_list()
        except:
            logger.info("exiting at check process list stage...")
            pass

    # list remote processor groups
    def remote_processors(self, root_process_group_id):
        self.root_process_group_id = root_process_group_id
        cmd_to_run="curl -s -X GET %s/process-groups/%s/remote-process-groups|  jq \'.\' | grep \'\"id\"\'|awk \
        \'{print $2}\'|uniq" % (self.nifi_api_url, self.root_process_group_id)
        logger.debug("cmd to list of Remote Process Groups: %s", cmd_to_run)
        proc = subprocess.Popen(cmd_to_run, stdout=subprocess.PIPE, shell=True)
        (cmd, err) = proc.communicate()
        logger.info("remote process group: \n%s", cmd_to_run)
        self.remote_process_group_list.append(cmd)
        logger.debug("REMOTE PROCESSOR GROUP LIST (destinationGroupId): %s", self.remote_process_group_list)
        #raise SystemExit

    # setup communication with RPG
    def setup_communication(self, remote_id, rpg_id, route_on_attribute_id, root_proc_grp):
        comm_route_rpg = "curl -s -XPOST '%s/process-groups/%s/connections' \
        -H 'Content-Type: application/json' \
        --data-binary '{\"revision\":{\"version\":0}, \"component\":{\"source\":{\"id\":\"%s\", \"groupId\":\"%s\",\"type\":\"PROCESSOR\"},\"destination\":{ \"id\":\"%s\",\"groupId\":\"%s\",\"type\":\"REMOTE_INPUT_PORT\"},\"selectedRelationships\":[\"isConfigFile\"]}}'" \
        % (self.nifi_api_url, root_proc_grp, route_on_attribute_id, root_proc_grp, remote_id, rpg_id)
        proc = subprocess.Popen(comm_route_rpg, stdout=subprocess.PIPE, shell=True)
        logger.info("setup communcation: %s", comm_route_rpg)
        proc.communicate()

    def setup_communication_custom(self, root_proc_grp, remote_id, rpg_id, type, source_id, source_process_group):
        comm_route_rpg_custom = "curl -s -XPOST '%s/process-groups/%s/connections' -H 'Origin: %s' \
        -H 'Accept-Encoding: gzip, deflate' -H 'Content-Type: application/json' -H 'Accept: application/json' \
        --data-binary '{\"revision\":{\"version\":0}, \"component\":{\"source\":{\"id\":\"%s\", \"groupId\":\"%s\",\"type\":%s},\"destination\":{ \"id\":\"%s\",\"groupId\":\"%s\",\"type\":\"REMOTE_INPUT_PORT\"}}}' --compressed" \
        % (self.nifi_api_url, root_proc_grp, self.nifi_api_url, remote_id, rpg_id, type, source_id, source_process_group)
        proc22 = subprocess.Popen(comm_route_rpg_custom, stdout=subprocess.PIPE, shell=True)
        logger.debug("setup communcation (custom): \n%s", comm_route_rpg_custom)
        proc22.communicate()

    def get_component_id(self, list_of_remote_processor_groups):
        self.list_of_remote_processor_groups = list_of_remote_processor_groups
        #for i in list_of_remote_processor_groups:
        logger.info("remote processor group: %s", list_of_remote_processor_groups)
        comp_id = "curl -s -X GET %s/remote-process-groups/%s| jq \'.\' | grep \'\"id\"\'|awk \
        \'{print $2}\'|uniq" % (self.nifi_api_url, list_of_remote_processor_groups)
        logger.info("cmd to list component id:", comp_id)
        proc = subprocess.Popen(comp_id, stdout=subprocess.PIPE, shell=True)
        logger.info("component id: %s", comp_id)
        (cmd1, err) = proc.communicate()
        self.component_id_list.append(cmd1)
        #logger.debug("LIST OF COMPONENT ID (destinationId): \n%s", self.component_id_list)
        #raise SystemExit

    def start_remote_process_grp(self, comp_id, api_url):
        cmd_to_enable_remote_process_group = "curl '%s/remote-process-groups/%s' -X PUT -H 'Origin: %s' -H 'Content-Type: application/json' \
        --data-binary '{\"revision\": {\"clientId\":\"%s\",\"version\":0}, \"component\": {\"id\": \"%s\", \"transmitting\": \"true\"}}'" \
        % (self.nifi_api_url, comp_id, api_url, 'client_id', comp_id)
        logger.debug("cmd to start_remote_process_grp: ", cmd_to_enable_remote_process_group)
        proc = subprocess.Popen(cmd_to_enable_remote_process_group, stdout=subprocess.PIPE, shell=True)
        logger.info("start_remote_process_grp: \n%s", cmd_to_enable_remote_process_group)
        proc.communicate()

    # list output host ports
    def list_output_host_port(self):
        list_of_output_ports = "curl -s -X GET %s/resources | jq \'.\' | grep \'\"NIFI_OUTPUT_PORT\"\'|awk \'{print $2}\'\
        |uniq" % (self.nifi_api_url)
        proc = subprocess.Popen(list_of_output_ports, stdout=subprocess.PIPE, shell=True)
        (list_of_output_ports, err) = proc.communicate()
        self.output_ports_list.append(list_of_output_ports.splitlines())

    # get ouput host port type
    def get_host_output_port_type(self, output_port):
        host_port_type = "curl -s -X GET %s/ouput-ports/%s | jq \'.\' | egrep \'REMOTE_PORT|\"id\"\'|uniq |tail -2" % \
        (self.nifi_api_url, output_port)
        #logger.info("cmd output port: %s", host_port_type)
        proc = subprocess.Popen(host_port_type , stdout=subprocess.PIPE, shell=True)
        (get_host_port_type , err) = proc.communicate()
        self.get_output_port_list.append(get_host_port_type)

    # list of input host ports
    def list_input_host_port(self, list_of_processors):
        self.list_of_processors = list_of_processors
        cmd_to_run = "curl -s -X GET %s/process-groups/%s/input-ports | jq \'.\' | grep \'\"id\"\'|awk \'{print $2}\'\
        |uniq" % (self.nifi_api_url, self.list_of_processors)
        proc = subprocess.Popen(cmd_to_run, stdout=subprocess.PIPE, shell=True)
        (cmd, err) = proc.communicate()
        self.list_input_host_port_list.append(cmd.splitlines())
        #raise SystemExit

    # get input host port version
    def get_host_input_port_version(self, input_port):
        self.input_port = input_port
        get_host_port_version = "curl -s -X GET %s/input-ports/%s | jq \'.\' | grep \'\"version\"\'|awk \'{print $2}\'|head -1" % \
        (self.nifi_api_url, self.input_port)
        proc = subprocess.Popen(get_host_port_version , stdout=subprocess.PIPE, shell=True)
        (get_host_port_version , err) = proc.communicate()
        self.get_host_port_version.update({self.input_port:get_host_port_version })

    # get input host port type
    def get_host_input_port_type(self, input_port):
        self.input_port = input_port
        host_port_type = "curl -s -X GET %s/input-ports/%s | jq \'.\' | egrep \'REMOTE_PORT|\"id\"\'|uniq |tail -2" % \
        (self.nifi_api_url, self.input_port)
        #logger.info("cmd run: \n%s", host_port_type)
        proc = subprocess.Popen(host_port_type , stdout=subprocess.PIPE, shell=True)
        (get_host_port_type , err) = proc.communicate()
        self.get_host_port_type.append(get_host_port_type)

    # get RouteOnAttribute_port_id
    def get_RouteOnAttribute_port_id(self, input_port):
        self.input_port = input_port
        RouteOnAttribute = "curl -s -X GET %s/process-groups/%s | jq \'.\' | grep RouteOnAttribute" % \
        (self.nifi_api_url, self.input_port)
        logger.info("cmd run RouteOnAttribute_port: \n%s", RouteOnAttribute)
        proc = subprocess.Popen(RouteOnAttribute , stdout=subprocess.PIPE, shell=True)
        (RouteOnAttribute1 , err) = proc.communicate()
        self.get_RouteOnAttribute_port_id_list.append(RouteOnAttribute1)

    # enable input host ports
    def enable_input_host_port(self, list_input_host_port, get_version):
        self.list_input_host_port = list_input_host_port
        self.get_version = get_version
        enable_input_port_cmd = "curl -s -o /dev/null -i -H 'Content-Type: application/json' -XPUT -d '{ \"status\": \
        { \"runStatus\": \"RUNNING\" }, \"component\": { \"state\": \"RUNNING\", \"id\": \"%s\"}, \
        \"id\": \"%s\", \"revision\": { \"clientId\": \"%s\", \"version\": %s } }' %s/input-ports/%s" \
        % (self.list_input_host_port, self.list_input_host_port, self.list_input_host_port,  self.get_version, self.nifi_api_url, self.list_input_host_port)
        subprocess.call(enable_input_port_cmd, stdout=subprocess.PIPE, shell=True)

    # list all controller services
    def list_controller_services(self, list_of_controller_services):
        self.list_of_controller_services = list_of_controller_services
        list_controller="curl -s -X GET %s/flow/process-groups/%s/controller-services| jq \'.\' \
        | grep \'\"id\"\'|awk \'{print $2}\'|uniq" % (self.nifi_api_url, self.list_of_controller_services)
        proc = subprocess.Popen(list_controller, stdout=subprocess.PIPE, shell=True)
        logger.info("list of controller services: \n%s", list_controller)
        (list_controller, err) = proc.communicate()
        logger.info("list controller services list: \n%s", list_controller)
        self.list_ctrl_services.append(list_controller)
        #return list_controller

    # get latest version for controller services
    def get_controller_services_version(self, controller_services):
        self.controller_services = controller_services
        get_controller_services_version = "curl -s -X GET %s/controller-services/%s| jq '.'|grep version| awk '{print $2}'|head -1" % (self.nifi_api_url, self.controller_services.strip())
        get_controller_services = subprocess.Popen(get_controller_services_version, stdout=subprocess.PIPE, shell=True)
        (get_controller_services_version, err) = get_controller_services.communicate()
        self.controller_services_version.update({self.controller_services:get_controller_services_version})

    # enable controller services
    def enable_controller_services(self, list_of_controller_services):
        logger.info("staring controller services")
        self.list_of_controller_services = list_of_controller_services
        self.controller_version = '0'
        stripped_list = self.list_of_controller_services.strip('\n')
        enable_controller = "curl --max-time 120 -s -i -H 'Content-Type: application/json' -XPUT -d '{\"id\": \"%s\",\
        \"component\":{\"id\": \"%s\",\"state\": \"ENABLED\"}, \"revision\":{\"clientId\": \
        \"%s\", \"version\":%s}}' %s/controller-services/%s" \
        % (stripped_list, stripped_list, stripped_list, self.controller_version, self.nifi_api_url, stripped_list)
        logger.debug("controller services startup command: \n %s", enable_controller)
        proc = subprocess.Popen(enable_controller, stdout=subprocess.PIPE, shell=True)
        proc.communicate()

    # get process groups version
    def get_process_groups_version(self, process_group):
        self.process_group = process_group
        get_version = "curl -s -X GET %s/process-groups/%s | jq \'.\' | grep \'\"version\"\'|awk \'{print $2}\'|head -1" % \
        (self.nifi_api_url, self.process_group)
        proc = subprocess.Popen(get_version, stdout=subprocess.PIPE, shell=True)
        (get_version, err) = proc.communicate()
        self.process_groups_version.update({self.process_group:get_version})

    # enable process groups
    def enable_process_groups(self, proc_grp):
        self.proc_grp = proc_grp
        enable_processor_group = "curl -s -i -H 'Content-Type: application/json' -XPUT -d '\
        {\"id\":\"%s\",\"state\":\"RUNNING\"}' %s/flow/process-groups/%s" \
        % (self.proc_grp, self.nifi_api_url, self.proc_grp)
        subprocess.call(enable_processor_group, stdout=subprocess.PIPE, shell=True)

    # verify if nifi is reachable
    def system_status(self):
        system_status = "curl -s -XGET %s/system-diagnostics|jq \'.\'| grep \"buildTimestamp\" |awk \'{print $2}\'" % self.nifi_api_url
        proc = subprocess.Popen(system_status, stdout=subprocess.PIPE, shell=True)
        (cmd, err) = proc.communicate()
        return cmd

    def check_if_template_is_running(self):
        upload_template_url = "curl -s -XGET %s/flow/templates|jq '.' |grep id" % self.nifi_api_url
        validate_template_existance = subprocess.Popen(upload_template_url, stdout=subprocess.PIPE, shell=True)
        (validate_if_template_is_running, err) = validate_template_existance.communicate()
        if "id".encode() in validate_if_template_is_running:
            logger.debug("template already running...")
            raise SystemExit
        else:
            logger.debug("continue...")

    # list remote processor groups
    def remote_processors(self, root_process_group_id):
        self.root_process_group_id = root_process_group_id
        cmd_to_run="curl -s -X GET %s/process-groups/%s/remote-process-groups|  jq \'.\' | grep \'\"id\"\'|awk \
        \'{print $2}\'|uniq" % (self.nifi_api_url, self.root_process_group_id)
        proc = subprocess.Popen(cmd_to_run, stdout=subprocess.PIPE, shell=True)
        (cmd, err) = proc.communicate()
        logger.info("remote process group: \n%s", cmd_to_run)
        self.remote_process_group_list.append(cmd)
