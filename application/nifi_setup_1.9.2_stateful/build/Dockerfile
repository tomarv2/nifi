FROM apache/nifi:1.9.2

MAINTAINER varuntomar2019@gmail.com

USER root

LABEL type=nifi

RUN apt-get update && apt-get install -y \
     vim \
     wget \
     sudo \
     software-properties-common \
     git \
     telnet \
     nmap \
     net-tools \
     cron \
     python \
     jq \
     python3.5 \
     python-pip \
     python3-pip \
     dnsutils

RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
RUN python get-pip.py
RUN pip3 install requests

# ---------------------
# Custom processors
RUN mkdir -p /opt/jdbc/drivers
ADD ./custom_processors/ojdbc8.jar /opt/jdbc/drivers/
ADD ./custom_processors/RedshiftJDBC42-1.2.16.1027.jar /opt/jdbc/drivers/
ADD ./custom_processors/nifi-prometheus-nar-1.3.0.nar /opt/nifi/nifi-1.9.0/lib/
ADD ./custom_processors/jtds-1.3.1.jar /opt/nifi/nifi-1.9.0/lib/
ADD ./custom_processors/postgresql-42.2.4.jar /opt/nifi/nifi-1.9.0/lib/
ADD ./custom_processors/custom-nifi-site-to-site-reporting-nar-1.9.0.nar /opt/nifi/nifi-1.9.0/lib/
ADD ./custom_processors/jmx_prometheus_javaagent-0.3.1.jar /opt/nifi/nifi-1.9.0/lib/
#-----------------------
# Prometheus jmx exporter standard across all java application
ADD ./custom_processors/prometheus_jmx_exporter.yml /tmp/
#-----------------------
# Deployment scripts
ADD deploy/* /opt/deploy/
RUN pip3 install -r /opt/deploy/requirements.txt
RUN chown -R nifi:nifi /opt/deploy
#-----------------------

ADD ./deploy/nifi.sh /opt/nifi/nifi-1.9.0/bin/
RUN chmod +x /opt/nifi/nifi-1.9.0/bin/nifi.sh
