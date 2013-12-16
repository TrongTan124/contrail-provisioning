#!/usr/bin/env bash

# Copyright 2012 OpenStack LLC
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.


CONF_DIR=/etc/contrail
set -x

function error_exit
{
    echo "${PROGNAME}: ${1:-''} ${2:-'Unknown Error'}" 1>&2
    exit ${3:-1}
}

chkconfig mysqld 2>/dev/null
ret=$?
if [ $ret -ne 0 ]; then
    echo "MySQL is not enabled, enabling ..."
    chkconfig mysqld on 2>/dev/null
fi

service mysqld status 2>/dev/null
ret=$?
if [ $ret -ne 0 ]; then
    echo "MySQL is not active, starting ..."
    service mysqld restart 2>/dev/null
fi

# Use MYSQL_ROOT_PW from the environment or generate a new password
if [ ! -f $CONF_DIR/mysql.token ]; then
    if [ -n "$MYSQL_ROOT_PW" ]; then
	MYSQL_TOKEN=$MYSQL_ROOT_PW
    else
	MYSQL_TOKEN=$(openssl rand -hex 10)
    fi
    echo $MYSQL_TOKEN > $CONF_DIR/mysql.token
    chmod 400 $CONF_DIR/mysql.token
    echo show databases |mysql -u root &> /dev/null
    if [ $? -eq 0 ] ; then
        mysqladmin password $MYSQL_TOKEN
    else
        error_exit ${LINENO} "MySQL root password unknown, reset and retry"
    fi
else
    MYSQL_TOKEN=$(cat $CONF_DIR/mysql.token)
fi

source /etc/contrail/ctrl-details

# Check if ADMIN/SERVICE Password has been set
ADMIN_TOKEN=${ADMIN_TOKEN:-contrail123}
SERVICE_TOKEN=${SERVICE_TOKEN:-$(cat $CONF_DIR/service.token)}

cat > $CONF_DIR/openstackrc <<EOF
export OS_USERNAME=admin
export OS_PASSWORD=$ADMIN_TOKEN
export OS_TENANT_NAME=admin
export OS_AUTH_URL=http://127.0.0.1:5000/v2.0/
export OS_NO_CACHE=1
EOF

for APP in nova; do
  openstack-db -y --init --service $APP --rootpw "$MYSQL_TOKEN"
done

export ADMIN_TOKEN
export SERVICE_TOKEN

# Update all config files with service username and password
for svc in nova; do
    openstack-config --set /etc/$svc/$svc.conf keystone_authtoken admin_tenant_name service
    openstack-config --set /etc/$svc/$svc.conf keystone_authtoken admin_user $svc
    openstack-config --set /etc/$svc/$svc.conf keystone_authtoken admin_password $SERVICE_TOKEN
done

openstack-config --set /etc/nova/nova.conf DEFAULT quantum_admin_tenant_name service
openstack-config --set /etc/nova/nova.conf DEFAULT quantum_admin_username quantum
openstack-config --set /etc/nova/nova.conf DEFAULT quantum_admin_password $SERVICE_TOKEN
openstack-config --set /etc/nova/nova.conf DEFAULT quantum_url http://$QUANTUM:9696/
openstack-config --set /etc/nova/nova.conf DEFAULT quantum_url_timeout 300
openstack-config --set /etc/nova/nova.conf DEFAULT security_group_api quantum
openstack-config --set /etc/nova/nova.conf DEFAULT osapi_compute_workers 40
openstack-config --set /etc/nova/nova.conf DEFAULT service_quantum_metadata_proxy True
# openstack-config --set /etc/nova/nova.conf DEFAULT quantum_metadata_proxy_shared_secret contrail
openstack-config --set /etc/nova/nova.conf conductor workers 40

openstack-config --set /etc/nova/nova.conf DEFAULT compute_driver libvirt.LibvirtDriver

# Hack till we have synchronized time (config node as ntp server). Without this
# utils.py:service_is_up() barfs and instance deletes not fwded to compute node
openstack-config --set /etc/nova/nova.conf DEFAULT service_down_time 100000

openstack-config --set /etc/nova/nova.conf DEFAULT sql_max_retries -1

openstack-config --set /etc/nova/nova.conf DEFAULT novncproxy_port 5999
openstack-config --set /etc/nova/nova.conf DEFAULT novncproxy_host 0.0.0.0

openstack-config --set /etc/nova/nova.conf DEFAULT quota_instances 100000
openstack-config --set /etc/nova/nova.conf DEFAULT quota_cores 100000
openstack-config --set /etc/nova/nova.conf DEFAULT quota_ram 10000000

echo "======= Enabling the services ======"

for svc in qpidd httpd memcached; do
    chkconfig $svc on
done

for svc in api objectstore scheduler cert consoleauth novncproxy conductor; do
    chkconfig openstack-nova-$svc on
done

echo "======= Starting the services ======"

for svc in qpidd httpd memcached; do
    service $svc restart
done

for svc in api objectstore scheduler cert consoleauth novncproxy conductor; do
    service openstack-nova-$svc restart
done
