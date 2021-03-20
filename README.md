<p align="center">
    <a href="https://www.apache.org/licenses/LICENSE-2.0" alt="GitHub tag">
        <img src="https://img.shields.io/github/license/tomarv2/nifi" /></a>
    <a href="https://github.com/tomarv2/nifi/tags" alt="GitHub tag">
        <img src="https://img.shields.io/github/v/tag/tomarv2/nifi" /></a>
    <a href="https://stackoverflow.com/users/6679867/tomarv2" alt="Stack Exchange reputation">
        <img src="https://img.shields.io/stackexchange/stackoverflow/r/6679867"></a>
    <a href="https://discord.gg/XH975bzN" alt="chat on Discord">
        <img src="https://img.shields.io/discord/813961944443912223?logo=discord"></a>
    <a href="https://twitter.com/intent/follow?screen_name=varuntomar2019" alt="follow on Twitter">
        <img src="https://img.shields.io/twitter/follow/varuntomar2019?style=social&logo=twitter"></a>
</p>

## NiFi deployment & CICD

<p align="center">
  <img src="https://files.gitter.im/tomarv2/gEzT/nifi_jenkins.png">
</p>

Deploy a NiFi cluster as StatefulSet in k8s and continuous deployment of applications.

***
Covering two use cases:
- Setting up NiFi in minikube (this is what we provide to developers as a playground).
- Production ready deployment.

***
When we initially started deploying NiFi it was version on 1.5, k8s support for NiFi was not that great.
Things have changed a lot since then.

***
### This repo addresses two main concerns:

1. How to Deploy NiFi as a StatefulSet application
2. How to do CICD

***
### Pre-reqs
- k8s cluster
- Zookeeper to maintain NiFi state outside cluster
- Persistent disk
- Prometheus 
  - Two good options for exporting nifi metrics in prometheus supported format:
    - https://github.com/msiedlarek/nifi_exporter - haven't tried it as yet
    - https://github.com/mkjoerg/nifi-prometheus-reporter - tested & in use
***
### Repo structure

:wave: Repo is divided into two parts: "k8s stateful deployment" and "building NiFi docker image".

- `_kube`: k8s cluster deployment related files

- `_kube/config`: Properties files

- `_kube/templates`: templates (in xml format)

- `application/nifi_setup_1.11.4_stateful/build/deploy`: All scripts for building the NiFi docker image reside 

- `application/nifi_setup_1.11.4_stateful/build/custom_processors`: All custom processors jar files

***
### CICD process

- As NiFi is a stateful app, had to make some adjustments to our rollout, with every run:

#### Delete Statefulset app

```
sh "kubectl delete --namespace=${env.NameSpace} --server='https://qak8s-master.demo.com' --username=${k8s_user} --password=${k8s_pwd} --insecure-skip-tls-verify=true statefulsets ${env.serviceName} --cascade=false"
```

***
#### Delete Statefulset pods

```
sh "kubectl delete --server='https://qak8s-master.demo.com' --username=${k8s_user} --password=${k8s_pwd}  --insecure-skip-tls-verify=true pods -l cluster=${env.serviceName} -n ${env.NameSpace} --force --grace-period=0"
```

***
#### Delete PVC

```
sh "kubectl delete --server='https://qak8s-master.demo.com' --username=${k8s_user} --password=${k8s_pwd}  --insecure-skip-tls-verify=true pvc -l cluster=${env.serviceName} -n ${env.NameSpace} "
```

***
#### Deploy Statefulset

```
steps {
    script {
        try {
            withCredentials([usernamePassword(credentialsId: 'k8s_cluster_pwd_qa', passwordVariable: 'k8s_pwd', usernameVariable: 'k8s_user')]) {
                sh "kubectl create --namespace=${env.NameSpace} --server='https://qak8s-master.demo.com' --username=${k8s_user} --password=${k8s_pwd} --insecure-skip-tls-verify=true -f _kube/qa/statefulset.yaml"
                sh("eval \$(kubectl describe svc ${env.serviceName} --namespace=${env.NameSpace} --server='https://qak8s-master.demo.com' --username=${k8s_user} --password=${k8s_pwd} --insecure-skip-tls-verify=true |grep -i nodeport |grep -i web |grep -v hook |awk {'print \$3'}|cut -f1 -d '/' > NodePort)")
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
### How to run

    - python deploy_nifi.py <nifi_url> <repo location of templates> <template_name><project_name>
    
    - python deploy_nifi.py http://nifi.services.demo.com:80 http://varun.demo.com/projects/raw/templates nifi-template.xml application_name

***
### Note:

- We are also using a headless service

- We expose nifi metrics in prometheus format

- Update  `_kube/statefulset.yaml` with right information

- You will notice the `annotations` in `Statefulset.yaml` file, we are exporting metrics and logs to Datadog

- `nifi_setup_1.11.4_stateful/build/deploy/nifi.sh` points to custom `logback.xml` file

- Custom `logback.xml` to handle log in log issue with nifi logs(not sure if this is resolved in the latest version)

- `statefulset.yaml` is highly commented to work in minikube or in prod cluster with minimal changes

- Currently it works with `SecurityContext` will be changing it to work with PSP

***
#### Tip

:wave: The best way to use k8s related files just search and replace `sample-sync` with the required name and you are ready to go.

***
### Minikube setup

```
demo$ minikube service list
|----------------------|---------------------------|--------------|--------------------------------|
|      NAMESPACE       |           NAME            | TARGET PORT  |              URL               |
|----------------------|---------------------------|--------------|--------------------------------|
| default              | kubernetes                | No node port |
| devops               | sample-sync               |              | http://192.168.64.2:32403      |
|                      |                           |              | http://192.168.64.2:31162      |
|                      |                           |              | http://192.168.64.2:32383      |
|                      |                           |              | http://192.168.64.2:32412      |
| devops               | sample-sync-headless      | No node port |
| kube-system          | kube-dns                  | No node port |
| kubernetes-dashboard | dashboard-metrics-scraper | No node port |
| kubernetes-dashboard | kubernetes-dashboard      | No node port |
|----------------------|---------------------------|--------------|--------------------------------|
```

### Enable ingress on minikube

```
demo$ minikube addons enable ingress
The 'ingress' addon is enabled
```

### Headless service

:wave: A Headless Service is a service when you don’t need load-balancing and a single Service IP. Instead of load-balancing it will return the IPs of the attached Pod. Headless Services do not have a Cluster IP associated. Request will not be proxied by kube-proxy, instead NiFi will handle the service discovery.

<p align="center">
  <img src="https://files.gitter.im/tomarv2/KRXn/Screen-Shot-2020-04-12-at-6.33.46-PM.png">
</p>


#### Note:

:wave: If you find any issues or wants to see anything specific please open an issue.
