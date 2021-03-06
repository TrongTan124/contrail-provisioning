import string

template = string.Template("""
#
# Vnswad configuration options
#

[CONTROL-NODE]
# List of control-node's with ip1:port ip2:port format
servers=$__contrail_control_node_list__

[DEFAULT]
# Everything in this section is optional

# IP address and port to be used to connect to collector. 
# Multiple IP:port strings separated by space can be provided
collectors=$__contrail_collectors__

# Agent mode : can be vrouter / tsn / tor (default is vrouter)
# agent_mode=

# Enable/disable debug logging. Possible values are 0 (disable) and 1 (enable)
# debug=0

# Aging time for flow-records in seconds
# flow_cache_timeout=0

# Hostname of compute-node. If this is not configured value from `hostname`
# will be taken
# hostname=

# Http server port for inspecting vnswad state (useful for debugging)
# http_server_port=8085

# Category for logging. Default value is '*'
# log_category=

# Local log file name
log_file=/var/log/contrail/contrail-vrouter-agent.log

# Log severity levels. Possible values are SYS_EMERG, SYS_ALERT, SYS_CRIT, 
# SYS_ERR, SYS_WARN, SYS_NOTICE, SYS_INFO and SYS_DEBUG. Default is SYS_DEBUG
log_level=SYS_NOTICE

# Enable/Disable local file logging. Possible values are 0 (disable) and 1 (enable)
log_local=1

# Encapsulation type for tunnel. Possible values are MPLSoGRE, MPLSoUDP, VXLAN
# tunnel_type=

# Enable/Disable headless mode for agent. In headless mode agent retains last
# known good configuration from control node when all control nodes are lost.
# Possible values are true(enable) and false(disable)
# headless_mode=

# DHCP relay mode (true or false) to determine if a DHCP request in fabric
# interface with an unconfigured IP should be relayed or not
# dhcp_relay_mode=

# DPDK or legacy work mode
platform=$__contrail_work_mode__

# Physical address of PCI used by dpdk
physical_interface_address=$__pci_dev__

# MAC address of device used by dpdk
physical_interface_mac=$__physical_interface_mac__

# UIO driver to use for DPDK
physical_uio_driver=igb_uio

# Gateway mode : can be server/ vcpe (default is none)
gateway_mode=$__gateway_mode__

[DNS]
# List of control-node's with ip1:port ip2:port format
servers=$__contrail_dns_node_list__

[HYPERVISOR]
# Everything in this section is optional

# Hypervisor type. Possible values are kvm, xen and vmware
type=$__hypervisor_type__
vmware_mode=$__hypervisor_mode__

# Link-local IP address and prefix in ip/prefix_len format (for xen)
# xen_ll_ip=

# Link-local interface name when hypervisor type is Xen
# xen_ll_interface=

# Physical interface name when hypervisor type is vmware
vmware_physical_interface=$__vmware_physical_interface__

[FLOWS]
# Everything in this section is optional

# Maximum flows allowed per VM (given as % of maximum system flows)
# max_vm_flows=100
# Maximum number of link-local flows allowed across all VMs
# max_system_linklocal_flows=4096
# Maximum number of link-local flows allowed per VM
# max_vm_linklocal_flows=1024

# Number of threads for flow setup
# thread_count=1
thread_count=2

[TASK]
# Number of threads used by TBB
# thread_count=8

# Log message if time taken to execute task exceeds a threshold (in msec)
# log_exec_threshold=0
#
# Log message if time taken to schedule task exceeds a threshold (in msec)
# log_schedule_threshold=0
#
# TBB Keepawake timer interval (in msec)
# tbb_keepawake_timeout=20

[METADATA]
# Shared secret for metadata proxy service (Optional)
# metadata_proxy_secret=contrail

[NETWORKS]
# control-channel IP address used by WEB-UI to connect to vnswad to fetch
# required information (Optional)
control_network_ip=$__contrail_control_ip__

[VIRTUAL-HOST-INTERFACE]
# Everything in this section is mandatory

# name of virtual host interface
name=vhost0

# IP address and prefix in ip/prefix_len format
ip=$__contrail_vhost_ip__

# Gateway IP address for virtual host
gateway=$__contrail_vhost_gateway__

# Physical interface name to which virtual host interface maps to
physical_interface=$__contrail_physical_intf__

# We can have multiple gateway sections with different indices in the 
# following format
# [GATEWAY-0]
# Name of the routing_instance for which the gateway is being configured
# routing_instance=default-domain:admin:public:public

# Gateway interface name
# interface=vgw

# Virtual network ip blocks for which gateway service is required. Each IP
# block is represented as ip/prefix. Multiple IP blocks are represented by 
# separating each with a space
# ip_blocks=1.1.1.1/24

# [GATEWAY-1]
# Name of the routing_instance for which the gateway is being configured
# routing_instance=default-domain:admin:public1:public1

# Gateway interface name
# interface=vgw1

# Virtual network ip blocks for which gateway service is required. Each IP
# block is represented as ip/prefix. Multiple IP blocks are represented by 
# separating each with a space
# ip_blocks=2.2.1.0/24 2.2.2.0/24

# Routes to be exported in routing_instance. Each route is represented as
# ip/prefix. Multiple routes are represented by separating each with a space
# routes=10.10.10.1/24 11.11.11.1/24

[SERVICE-INSTANCE]
# Path to the script which handles the netns commands
netns_command=/usr/bin/opencontrail-vrouter-netns

# Number of workers that will be used to start netns commands
#netns_workers=1

# Timeout for each netns command, when the timeout is reached, the netns
# command is killed.
#netns_timeout=30

# [QOS]
# [QUEUE-1]
# Logical nic queues for qos config
# logical_queue=

# [QUEUE-2]
# Logical nic queues for qos config
# logical_queue=

# [QUEUE-3]
# This is the default hardware queue
# default_hw_queue= true

# Logical nic queues for qos config
# logical_queue=

# [QOS-NIANTIC]
# [PG-1]
# Scheduling algorithm for priority group (strict/rr)
# scheduling=

# Total hardware queue bandwidth used by priority group
# bandwidth=

# [PG-2]
# Scheduling algorithm for priority group (strict/rr)
# scheduling=

# Total hardware queue bandwidth used by priority group
# bandwidth=

# [PG-3]
# Scheduling algorithm for priority group (strict/rr)
# scheduling=

# Total hardware queue bandwidth used by priority group
# bandwidth=

""")
