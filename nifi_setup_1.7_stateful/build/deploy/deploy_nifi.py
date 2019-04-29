from controller_services import controller_services_list
from DeployTemplateBase import DeployTemplate
import time
from os import walk
import os
import shutil
import logging
import sys
from git import Repo
import re
import multiprocessing
import uuid

logger = logging.getLogger(__name__)
FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(format=FORMAT, level=os.environ.get("LOGLEVEL", "DEBUG"))
#logging.basicConfig(format=FORMAT, filename=LOG_FILENAME, filemode='w', level=logging.INFO)

api_url = sys.argv[1]
nifi_api_url = api_url + '/nifi-api'
service_name = sys.argv[2]
git_template_loc = sys.argv[3]


def my_random_string(string_length=10):
    random = str(uuid.uuid4())
    random = random.upper()
    random = random.replace("-","")
    return random[0:string_length]

#print(my_random_string(10))

pipeline_name = '/tmp/' + service_name + my_random_string(10)
logger.debug("-" * 50)
logger.debug('temporary directory: %s', pipeline_name)
download_dir = pipeline_name
logger.debug("-" * 50)
template_list = []

deploy_templates = DeployTemplate(nifi_api_url)


# enable controller services in parallel
def worker(ik):
    logger.debug("starting controller services: %s" %ik)
    deploy_templates.enable_controller_services(ik)


def enable_remote_process_group():
    try:
        logger.debug("starting remote process group...")
        for proc_group in deploy_templates.flatten(deploy_templates.final_list_of_processes):
            deploy_templates.enable_process_groups(proc_group)
    except:
        logger.debug("unable to start process group...")
        raise SystemExit

    try:
        logger.debug("deploy_templates.remote_process_group_list: \n%s", deploy_templates.remote_process_group_list)
        for item_in_remote_process_group_list in deploy_templates.remote_process_group_list:
            logger.debug("item_in_remote_process_group_list: %s", item_in_remote_process_group_list.split())
            for item_in_remote_process_group_list01 in item_in_remote_process_group_list.split():
                line = re.sub(r'"|,', '', item_in_remote_process_group_list01.decode('utf-8'))
                logger.debug("line: %s", line.lstrip())
                for _ in range(2):
                    logger.debug("remote process group: %s", line)
                    deploy_templates.start_remote_process_grp(line, api_url)
                    #time.sleep(5)
    except:
        #logger.debug("remote process group do not exist...")
        pass


def start_controller_services():
    try:
        logger.debug("\nlist of controller services:\n")
        jobs = []
        for c_service in controller_services_list(nifi_api_url):
            logger.debug("starting controller services (entering sleep)...")
            #time.sleep(2)
            p = multiprocessing.Process(target=worker, args=(c_service,))
            jobs.append(p)
            p.start()
    except:
        logger.debug("controller services do not exist...")
        pass


def start_process_group():
    #time.sleep(10)
    logger.debug("\nstarting process groups...")
    try:
        for proc_group in deploy_templates.flatten(deploy_templates.final_list_of_processes):
            deploy_templates.enable_process_groups(proc_group)
    except:
        logger.debug("unable to start process group...")
    logger.debug("process group started...")


def verify_if_template_is_running():
    logger.debug("\nvalidating if template(s) exists...\n")
    deploy_templates.validate_template()
    logger.debug("-" * 50)


# process group under root
def process_group_under_root():
    process_group_under_root = deploy_templates.process_grp_under_root(deploy_templates.root_process_grp())
    logger.debug("-" * 50)
    logger.debug("process group under root:\n %s", process_group_under_root)
    f = open(pipeline_name + '/process_under_root.txt', 'wb')
    f.write(process_group_under_root)
    f.close()


# list all process groups
def list_process_groups():
    deploy_templates.list_processor_grp(deploy_templates.process_grp_under_root(deploy_templates.root_process_grp()).splitlines())
    logger.debug("\nrunning check to gather all process groups...\n")
    deploy_templates.check_list()
    logger.debug("-" * 50)
    logger.debug("list of process group:\n%s", deploy_templates.flatten(deploy_templates.final_list_of_processes))
    logger.debug("-" * 50)
    deploy_templates.remote_processors(deploy_templates.root_process_grp())


def deploy_nifi_template():
    logger.info("verifying if template is already running...")
    deploy_templates.check_if_template_is_running()
    logger.debug('beginning template download from git...')
    try:
        logger.debug("trying to download..")
        if os.path.exists(download_dir):
            shutil.rmtree(download_dir)
        os.makedirs(download_dir)
    except:
        logger.debug("unable to download template from git...")

    Repo.clone_from(git_template_loc , download_dir)
    templates_list = []
    for (dirpath, dirnames, filenames) in walk(download_dir + '/templates'):
        templates_list.extend(filenames)
        break

    for files_to_upload in templates_list:
        try:
            logger.debug("-" * 50)
            logger.debug("files to upload: \n%s", files_to_upload)
            deploy_templates.upload_template(files_to_upload, download_dir)
            logger.debug("-" * 50)
        except:
            logger.error("unable to upload templates...")
            raise SystemExit

    logger.debug("starting deployment...")
    root_proc_grp = deploy_templates.root_process_grp()
    logger.debug("root process group: %s", root_proc_grp)
    logger.debug("-" * 50)

    deploy_templates.get_template_id()
    temp_list = []
    try:
        for element in deploy_templates.template_id:
            parts = element.decode().split('\n')
            temp_list.append(parts)
    except:
        logger.debug("unable to upload template...")
        raise SystemExit

    # instantiate template
    try:
        new_list = [x for x in temp_list if x]
        for i in new_list:
            logger.debug("template name: %s", i)
            deploy_templates.instantiate_template(i)
    except:
        logger.debug("unable to instantiate...")
        raise SystemExit
    process_group_under_root()
    list_process_groups()
    logger.debug("enable remote process group/controller services/process group (repeated - 3 times)")
    time.sleep(30)
    for _ in range(3):
        enable_remote_process_group()
        time.sleep(5)
        start_controller_services()
        start_process_group()


def main():
    if not deploy_templates.system_status():
        logger.debug("waiting for cluster to be reachable...")
        time.sleep(10)
        main()
main()


if __name__ == "__main__":
    main()
    #time.sleep(5)
    verify_if_template_is_running()
    deploy_nifi_template()
