#!/usr/bin/env bash

# add zip user
groupadd -g 600 zip
useradd -u 600 -g 600 zip
sudo sh -c "echo 'nifi ALL=(ALL)NOPASSWD:ALL' >> /etc/sudoers"

# update DNS
sudo sh -c "echo 'nameserver 10.10.19.6' >> /etc/resolv.conf"

path=/opt/nifi/nifi-1.11.4

# ------------------------
# move to persistent storage
sed -i -e "s|^nifi.flow.configuration.file=./conf/flow.xml.gz.*$|nifi.flow.configuration.file=/mnt/conf/flow.xml.gz|" $path/conf/nifi.properties
sed -i -e "s|^nifi.flow.configuration.archive.dir=./conf/archive/.*$|nifi.flow.configuration.archive.dir=/mnt/conf/archive/|" $path/conf/nifi.properties
sed -i -e "s|^nifi.templates.directory=./conf/templates.*$|nifi.templates.directory=/mnt/conf/templates|" $path/conf/nifi.properties

#sed -i -e "s|^nifi.database.directory=./database_repository.*$|nifi.database.directory=/mnt/database_repository|" $path/conf/nifi.properties
#sed -i -e "s|^nifi.flowfile.repository.directory=./flowfile_repository.*$|nifi.flowfile.repository.directory=/mnt/flowfile_repository|" $path/conf/nifi.properties
#sed -i -e "s|^nifi.content.repository.directory.default=./content_repository.*$|nifi.content.repository.directory.default=/mnt/content_repository|" $path/conf/nifi.properties
#sed -i -e "s|^nifi.provenance.repository.directory.default=./provenance_repository.*$|nifi.provenance.repository.directory.default=/mnt/provenance_repository|" $path/conf/nifi.properties

# ----------------------
sed -i -e "s|^nifi.web.http.host=.*$|nifi.web.http.host=`hostname -i`|" $path/conf/nifi.properties
sed -i -e "s|^nifi.remote.input.host=.*$|nifi.remote.input.host=`hostname -i`|" $path/conf/nifi.properties
sed -i -e "s|^nifi.cluster.node.address=.*$|nifi.cluster.node.address=`hostname -i`|" $path/conf/nifi.properties
sed -i -e "s|^nifi.cluster.flow.election.max.wait.time=.*$|nifi.cluster.flow.election.max.wait.time=1 min|" $path/conf/nifi.properties
sed -i -e "s|^nifi.cluster.is.node=.*$|nifi.cluster.is.node=true|" $path/conf/nifi.properties
sed -i -e "s|^nifi.cluster.node.protocol.port=.*$|nifi.cluster.node.protocol.port=8082|" $path/conf/nifi.properties
sed -i -e "s|^nifi.cluster.node.connection.timeout=.*$|nifi.cluster.node.connection.timeout=30 sec|" $path/conf/nifi.properties
sed -i -e "s|^nifi.cluster.node.read.timeout=.*$|nifi.cluster.node.read.timeout=30 sec|" $path/conf/nifi.properties
sed -i -e "s|^nifi.cluster.node.connection.timeout=.*$|nifi.cluster.node.connection.timeout=30 sec|" $path/conf/nifi.properties
sed -i -e "s|^nifi.cluster.node.read.timeout=.*$|nifi.cluster.node.read.timeout=30 sec|" $path/conf/nifi.properties
sed -i -e "s|^nifi.components.status.snapshot.frequency=.*$|nifi.components.status.snapshot.frequency= 5 min|" $path/conf/nifi.properties
sed -i -e "s|^nifi.components.status.repository.buffer.size=.*$|nifi.components.status.repository.buffer.size= 288|" $path/conf/nifi.properties
sed -i -e "s|^nifi.provenance.repository.index.threads=.*$|nifi.provenance.repository.index.threads=4|" $path/conf/nifi.properties
sed -i -e "s|^nifi.provenance.repository.rollover.time=.*$|nifi.provenance.repository.rollover.time=1 min|" $path/conf/nifi.properties
sed -i -e "s|^nifi.provenance.repository.rollover.size=.*$|nifi.provenance.repository.rollover.size=1 GB|" $path/conf/nifi.properties
sed -i -e "s|^nifi.queue.swap.threshold=.*$|nifi.queue.swap.threshold=5000|" $path/conf/nifi.properties
sed -i -e "s|^nifi.swap.in.period=.*$|nifi.swap.in.period=10 sec|" $path/conf/nifi.properties
sed -i -e "s|^nifi.swap.in.threads=.*$|nifi.swap.in.threads=2|" $path/conf/nifi.properties
sed -i -e "s|^nifi.swap.out.period=.*$|nifi.swap.out.period=10 sec|" $path/conf/nifi.properties
sed -i -e "s|^nifi.swap.out.threads=.*$|nifi.swap.out.threads=8|" $path/conf/nifi.properties
sed -i -e "s|^nifi.zookeeper.connect.timeout=.*$|nifi.zookeeper.connect.timeout=5 secs|" $path/conf/nifi.properties
sed -i -e "s|^nifi.zookeeper.session.timeout=.*$|nifi.zookeeper.session.timeout=5 secs|" $path/conf/nifi.properties

# ------------------------
echo '*  hard  nofile  50000' >> /etc/security/limits.conf
echo '*  soft  nofile  50000' >> /etc/security/limits.conf
echo '*  hard  nproc  10000' >> /etc/security/limits.conf
echo '*  soft  nproc  10000' >> /etc/security/limits.conf
echo 'vm.swappiness = 0'  >>  /etc/sysctl.conf

# ------------------------
# update bootstrap.conf
sed -i -e "s|^java.arg.2=.*$|java.arg.2=-Xms1g|" $path/conf/bootstrap.conf
sed -i -e "s|^java.arg.3=.*$|java.arg.3=-Xmx1g|" $path/conf/bootstrap.conf
echo 'java.arg.7=-XX:ReservedCodeCacheSize=256m' >> $path/conf/bootstrap.conf
echo 'java.arg.8=-XX:CodeCacheMinimumFreeSpace=10m' >> $path/conf/bootstrap.conf
echo 'java.arg.9=-XX:+UseCodeCacheFlushing'>> $path/conf/bootstrap.conf
# ------------------------
echo "####### Enabling JMX and Prometheus metrics setup #######" >> /opt/nifi/nifi-1.11.4/conf/bootstrap.conf;
echo "java.arg.101=-Dcom.sun.management.jmxremote.local.only=true" >> /opt/nifi/nifi-1.11.4/conf/bootstrap.conf;
echo "java.arg.102=-Dcom.sun.management.jmxremote" >> /opt/nifi/nifi-1.11.4/conf/bootstrap.conf;
echo "java.arg.103=-Dcom.sun.management.jmxremote.authenticate=false" >> /opt/nifi/nifi-1.11.4/conf/bootstrap.conf;
echo "java.arg.104=-Dcom.sun.management.jmxremote.ssl=false" >> /opt/nifi/nifi-1.11.4/conf/bootstrap.conf;
echo "java.arg.104=-Dcom.sun.management.jmxremote.port=30007" >> /opt/nifi/nifi-1.11.4/conf/bootstrap.conf;
echo "java.arg.105=-javaagent:/opt/nifi/nifi-1.11.4/lib/jmx_prometheus_javaagent-0.3.1.jar=8079:/tmp/prometheus_jmx_exporter.yml" >> /opt/nifi/nifi-1.11.4/conf/bootstrap.conf;
echo "####### Enabling JMX and Prometheus metrics setup #######" >> /opt/nifi/nifi-1.11.4/conf/bootstrap.conf;
# ------------------------
mkdir -p $path/state/zookeeper
touch $path/state/zookeeper/myid
echo `hostname -i|tr -d '.'` > $path/state/zookeeper/myid
