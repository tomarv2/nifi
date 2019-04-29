
**kubernetes-nifi-cluster**

A nifi cluster running in kubernetes

I have tested it in nifi 1.7, will try it with 1.9 soon.

**Prerequisites**

- A running zookeeper cluster, for production deployment I would recommend a 3 node zk cluzter

- This deploy NIFI on AWS EC2 k8s with PV

- All this exposes your nifi metrics in prometheus format in case you want to view them

- It also has custom logback.xml to handle log in log issue with nifi

**Files layout**

- k8s related files are in _kube directory

- All the scripts for deployment reside in build/deploy directory

- All the custom processors jar sit in build/custom_processors

- All properties file relating to the application reside in config


**Follow below steps to setup NiFi environment:**

How we deploy our NiFi stateful application on AWS k8s

- Update **line 54** in statefulset.yaml file (located under **_kube**) to point to the right url **(RAW URL)**

- Put your NiFi templates in **templates** directory and properties file in **config** directory

I am working on cleaning up jenkins functions and will posting them as well.

For any questions, please drop an email to devopsac@gmail.com

Note: there is some cleanup to do, i am going fix it soon, this files as it will work. I have been using them in production for over a year.
