#!/bin/bash  -v

#Script logging
exec > >(tee /var/log/post-launch-configs.log|logger -t user-data -s 2>/dev/console) 2>&1

#Enable, Start and Register Nessus Agent
systemctl enable nessusagent
systemctl start nessusagent
/opt/nessus_agent/sbin/nessuscli agent link --key=2c23ba1f248457878d13aa58ddedf544c0806c79f3a58b8c1a420d8d12cdbfcf --groups=NCI AWS EC2 Instances --host=cloud.tenable.com --port=443

#Enable, and Start BigFix Agent
systemctl enable besclient
systemctl start besclient

#Register CentOS EC2 Instance with Satellite Server
rm -f /etc/sysconfig/rhn/systemid
subscription-manager clean
subscription-manager register --org="Cloud_One_National_Cancer_Institute" --activationkey="nci-dev-centos7-x86_64-key"

#Subcribe EC2 Docker to the correct repository if succesful you should see
#"Successfully attached a subscription for: Docker CE x86_64"
subscription-manager attach --pool=8a50a677752719c401756aa744e80197

#Install Puppet agent
curl -k https://ncias-p1842-v.nci.nih.gov:8140/packages/current/install.bash | sudo bash

#Enable and Start ESET Antivirus Endpoint
systemctl enable esets
systemctl start esets

#Update/Patch OS to Latest Release
yum -y update
