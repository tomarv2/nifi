
**NiFi deployment**
***

How to deploy a NiFi Cluster (Stateful app in k8s)
***

**Pre-reqs**
- k8s cluster
- Zookeeper to maintain NiFi state outside cluster
- Persistent disk
- Prometheus
***

**How it works**

As part of the CICD process, user makes a commit to a branch and it triggers a build.

- As its stateful app, we had to make some adjustments to our rollout, with every run we are:

 - Delete the stateful app

```sh "kubectl delete --namespace=${env.NameSpace} --server='https://qak8s-master.tomarv2.com' --username=${k8s_user} --password=${k8s_pwd} --insecure-skip-tls-verify=true statefulsets ${env.serviceName} --cascade=false"```

***

-  Delete the stateful pods

```sh "kubectl delete --server='https://qak8s-master.aur.test.ziprealty.com' --username=${k8s_user} --password=${k8s_pwd}  --insecure-skip-tls-verify=true pods -l cluster=${env.serviceName} -n ${env.NameSpace} --force --grace-period=0"```

***

- Delete NiFi PVC

```sh "kubectl delete --server='https://qak8s-master.aur.test.ziprealty.com' --username=${k8s_user} --password=${k8s_pwd}  --insecure-skip-tls-verify=true pvc -l cluster=${env.serviceName} -n ${env.NameSpace} "```

***

- Deploy NiFi Statefulset:

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

- Tested with python 2.7
- When we initially started deploying NiFi it was version on 1.5, so k8s support was not that great.
Things have changed a lot and we haven't changed out deployment strategy too much as yet.

