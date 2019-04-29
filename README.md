
**kubernetes-nifi-cluster**

A nifi cluster running in kubernetes.

I have tested it in nifi 1.7, will try it with 1.9 soon.

**Prerequisites**

- A running zookeeper cluster, for production deployment I would recommend a 3 node zk cluzter

- This deploy NIFI on AWS EC2 k8s with PV or on k8s in VMWare

- All this exposes your nifi metrics in prometheus format in case you want to view them

- It also has custom logback.xml to handle log in log issue with nifi

**Files layout**

- k8s related files are in _kube directory

- All the scripts for deployment reside in build/deploy directory

- All the custom processors jar sit in build/custom_processors

- All properties files go in config directory

- All templates xml files go in templates directory


**Follow below steps to setup NiFi environment:**

How we deploy our NiFi stateful application on AWS k8s

- Update **line 54** in statefulset.yaml file (located under **_kube**) to point to the right url **(RAW URL)**

- Put your NiFi templates in **templates** directory and properties file in **config** directory

For any questions, please drop an email to devopsac@gmail.com

**How to Deploy**

- kubectl --kubeconfig kubeconfig.yaml apply --insecure-skip-tls-verify=true -f _kube/statefulset.yaml"
- sh "wget <repo_url>/build/deploy/controller_services.py"
- sh "wget <repo_url>/build/deploy/deploy_nifi.py"
- sh "wget <repo_url>/build/deploy/DeployTemplateBase.py"
- sh "wget <repo_url>/build/deploy/parse_yaml.py"
- sh "wget <repo_url>/build/deploy/setup_connection.py"
//sh "wget <repo_url>/build/deploy/requirements.txt"
- sh "curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py; sudo python get-pip.py"
- sh "sudo pip install gitpython"
- sh "sudo yum install -y epel-release jq"
//sh "sudo pip install -r requirements.txt"
- sh "python deploy_nifi.py ${nifiUrl} ${serviceName} ${WORKSPACE}" 
}

**Note**

There is some cleanup to do, this files will work as. I have been using them in production for over a year.
