#!/usr/bin/env groovy

@Library('pipeline-library') _

pipeline {

    agent { label 'engr' }

    options {
        disableConcurrentBuilds()
        timeout(time: 1, unit: 'HOURS')
        buildDiscarder(logRotator(numToKeepStr: '5'))
    }

    environment {
        channel                                 = "#vt-test"
        scmUrl                                  = sh(returnStdout: true, script: 'git config remote.origin.url').trim()
        nameSpace                               = 'engr'
        serviceName                             = 'sample-sync'
        Url                                     = "http://sample-sync.devops.com"
    }

    stages {
        stage('Start') {
            steps {
                sendStartBuildNotification(env.channel)
            }
        }
        stage('Prepare NiFi') {
            when {
                anyOf {
                    branch "master"
                }
            }
            steps {
                checkExistingStatefulset('prod', env.nameSpace)
                deleteStatefulset('prod', env.nameSpace, env.serviceName)
                deleteExistingPods('prod', env.nameSpace, env.serviceName)
                deletePVC('prod', env.nameSpace, env.serviceName)
                deployStatefulset('prod', env.nameSpace, env.serviceName)
            }
        }
        stage('NiFi Deploy Template') {
            when {
                anyOf {
                    branch "master"
                }
            }
            steps {
                deployNifiTemplate('prod', env.Url, env.serviceName)
                sh "echo 'NiFi Url: echo ${env.Url}/nifi/'"
            }
        }
    }
    post {
        always {
            sendEndBuildNotification(currentBuild.currentResult, env.channel)
        }
    }
}
