import string

template = string.Template("""
[DEFAULTS]
ifmap_server_ip=$__contrail_ifmap_server_ip__
ifmap_server_port=$__contrail_ifmap_server_port__
ifmap_username=$__contrail_ifmap_username__
ifmap_password=$__contrail_ifmap_password__
api_server_ip=$__contrail_api_server_ip__
api_server_port=$__contrail_api_server_port__
zk_server_ip=$__contrail_zookeeper_server_ip__
log_file=$__contrail_log_file__
cassandra_server_list=$__contrail_cassandra_server_list__
disc_server_ip=$__contrail_disc_server_ip__
disc_server_port=$__contrail_disc_server_port__

[SECURITY]
use_certs=$__contrail_use_certs__
keyfile=$__contrail_keyfile_location__
certfile=$__contrail_certfile_location__
ca_certs=$__contrail_cacertfile_location__

[KEYSTONE]
auth_host=$__contrail_keystone_ip__
admin_user=$__contrail_admin_user__
admin_password=$__contrail_admin_password__
admin_tenant_name=$__contrail_admin_tenant_name__
admin_token=$__contrail_admin_token__
""")
