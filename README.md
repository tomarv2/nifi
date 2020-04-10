
**NiFi deployment & CICD**

![Image description](https://files.gitter.im/tomarv2/Re3v/Screen-Shot-2020-04-10-at-3.38.16-PM.png)

***

Deploy a NiFi cluster as StatefulSet in k8s and continuous deployment of applications.

When we initially started deploying NiFi it was version on 1.5, so k8s support was not that great.
Things have changed a lot since then.

This repo addresses two main concerns:

1. How to Deploy NiFi as a StatefulSet application
2. How to do CICD

***

**Pre-reqs**
- k8s cluster
- Zookeeper to maintain NiFi state outside cluster
- Persistent disk
- Prometheus 
  - Two good options for exporting nifi metrics in prometheus supported format:
    - https://github.com/msiedlarek/nifi_exporter - haven't tried it as yet
    - https://github.com/mkjoerg/nifi-prometheus-reporter - tested & in use
***

**Repo structure**

Repo is divided into two parts: "k8s stateful deployment" and "building NiFi docker image".

- `_kube`: k8s cluster deployment related files

- `_kube/config`: Properties files

- `_kube/templates`: templates (in xml format)

- `application/nifi_setup_1.11.4_stateful/build/deploy`: All scripts for building the NiFi docker image reside 

- `application/nifi_setup_1.11.4_stateful/build/custom_processors`: All custom processors jar files
***

**CICD process**

- As its stateful app, we had to make some adjustments to our rollout, with every run:

 - Delete the Statefulset app

```sh "kubectl delete --namespace=${env.NameSpace} --server='https://qak8s-master.tomarv2.com' --username=${k8s_user} --password=${k8s_pwd} --insecure-skip-tls-verify=true statefulsets ${env.serviceName} --cascade=false"```

***

-  Delete the Statefulset pods

```sh "kubectl delete --server='https://qak8s-master.tomarv2.com' --username=${k8s_user} --password=${k8s_pwd}  --insecure-skip-tls-verify=true pods -l cluster=${env.serviceName} -n ${env.NameSpace} --force --grace-period=0"```

***

- Delete PVC

```sh "kubectl delete --server='https://qak8s-master.tomarv2.com' --username=${k8s_user} --password=${k8s_pwd}  --insecure-skip-tls-verify=true pvc -l cluster=${env.serviceName} -n ${env.NameSpace} "```

***

- Deploy Statefulset

```
steps {
    script {
        try {
            withCredentials([usernamePassword(credentialsId: 'k8s_cluster_pwd_qa', passwordVariable: 'k8s_pwd', usernameVariable: 'k8s_user')]) {
                sh "kubectl create --namespace=${env.NameSpace} --server='https://qak8s-master.tomarv2.com' --username=${k8s_user} --password=${k8s_pwd} --insecure-skip-tls-verify=true -f _kube/qa/statefulset.yaml"
                sh("eval \$(kubectl describe svc ${env.serviceName} --namespace=${env.NameSpace} --server='https://qak8s-master.tomarv2.com' --username=${k8s_user} --password=${k8s_pwd} --insecure-skip-tls-verify=true |grep -i nodeport |grep -i web |grep -v hook |awk {'print \$3'}|cut -f1 -d '/' > NodePort)")
                script {
                    env.NODEPORT = readFile('NodePort')
                    sh "cat NodePort"
                }
            }
        }
        catch (exc) {sh 'echo statefulset does not exist...'}
    }
}
```
***

- Deploy NiFi Template

***

- Deploy Monitoring

***

**How to run**

    - python deploy_nifi.py <nifi_url> <repo location of templates> <template_name><project_name>
    
    - python deploy_nifi.py http://nifi.services.tomarv2.com:80 http://varun.tomarv2.com/projects/raw/templates nifi-template.xml application_name

***
   
**Note**

- Tested with python 2.7 (Working on upgrading to work with 3.6)

- We are also using a headless service

- We expose nifi metrics in prometheus format

- Update  `_kube/statefulset.yaml` with right information

- You will notice the `annotations` in `Statefulset.yaml` file, we are exporting metrics and logs to Datadog

- `nifi_setup_1.11.4_stateful/build/deploy/nifi.sh` points to custom `logback.xml` file

- Custom `logback.xml` to handle log in log issue with nifi logs(not sure if this is resolved in the latest version)

***

**Tip**

- The best way to use k8s related files just search and replace `sample-sync` with the required name and you are ready to go.

