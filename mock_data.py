# mock_data.py

interfaces = {
    'ethernet': 'ethernet',
    'bonding': 'bonding',
    'bridge': 'bridge',
    'vlan': 'vlan',
    'eth_vlan': 'eth_vlan',
    'loopback': 'loopback',
    'switchport': 'switchport',
    'tunnel': 'tunnel',
    'wlan': 'wlan'
}

# Примеры имён интерфейсов для каждого типа
interface_names = {
    'ethernet': ['eth0', 'eth1', 'eth2', 'eth3'],
    'bonding': ['bond0', 'bond1', 'bond2'],
    'bridge': ['br0', 'br1', 'br2'],
    'vlan': ['vlan10', 'vlan20', 'vlan30'],
    'eth_vlan': ['eth0.10', 'eth1.20', 'eth2.30'],
    'loopback': ['lo0', 'lo1'],
    'switchport': ['switchport1', 'switchport2', 'switchport3'],
    'tunnel': ['tunnel0', 'tunnel1', 'tunnel2'],
    'wlan': ['wlan0', 'wlan1']
}

# Примеры VLAN ID
vlan_ids = [10, 20, 30, 40, 50]

# Примеры MAC-адресов
mac_addresses = [
    "00:1A:2B:3C:4D:5E",
    "11:22:33:44:55:66",
    "AA:BB:CC:DD:EE:FF",
    "F0:F1:F2:F3:F4:F5"
]

# Примеры IP-адресов
ip_addresses = [
    "192.168.1.1",
    "10.0.0.1",
    "172.16.0.1",
    "192.168.100.1"
]

# Примеры MTU (Maximum Transmission Unit)
mtu_values = [1500, 9000, 1400, 1600]

# Примеры режимов туннеля
tunnel_modes = ["gre", "ipip", "gretap", "vti"]

# Примеры настроек очередей (queue settings)
queue_settings = {
    "tx": [100, 200, 300],
    "rx": [50, 100, 150]
}

# Примеры параметров STP (Spanning Tree Protocol)
stp_parameters = {
    "priority": [4096, 8192, 12288, 16384],
    "forward_delay": [15, 20, 30],
    "hello_time": [2, 4, 6],
    "max_age": [20, 40, 60]
}

# Примеры параметров RIP (Routing Information Protocol)
rip_parameters = {
    "version": [1, 2],
    "authentication_mode": ["text", "md5"],
    "split_horizon": [True, False]
}

# Примеры параметров OSPF (Open Shortest Path First)
ospf_parameters = {
    "area_id": ["0.0.0.0", "1.1.1.1", "2.2.2.2"],
    "cost": [10, 100, 1000],
    "hello_interval": [10, 20, 30],
    "dead_interval": [40, 60, 120]
}

# Примеры параметров LLDP (Link Layer Discovery Protocol)
lldp_parameters = {
    "enabled": [True, False],
    "med_enabled": [True, False],
    "tx_interval": [30, 60, 120]
}

# Примеры параметров CARP (Common Address Redundancy Protocol)
carp_parameters = {
    "vip": ["192.168.1.100", "10.0.0.100"],
    "advbase": [1, 2, 3],
    "advskew": [0, 10, 20]
}

# Примеры параметров PoE (Power over Ethernet)
poe_parameters = {
    "power_limit": [15, 30, 60],
    "priority": ["low", "high"],
    "enabled": [True, False]
}

# Примеры параметров QoS (Quality of Service)
qos_parameters = {
    "egress_map": ["map1", "map2", "map3"],
    "ingress_map": ["imap1", "imap2", "imap3"]
}

# Примеры параметров ARP (Address Resolution Protocol)
arp_parameters = {
    "proxy_arp": [True, False],
    "announce": [True, False],
    "reply": [True, False]
}

# Примеры параметров DHCP
dhcp_parameters = {
    "lease_time": [3600, 7200, 14400],
    "default_gateway": ["192.168.1.1", "10.0.0.1"]
}

# Примеры параметров ISIS (Intermediate System to Intermediate System)
isis_parameters = {
    "metric": [10, 20, 30],
    "wide_metric": [True, False],
    "hello_interval": [3, 5, 10]
}

# Примеры параметров LDP (Label Distribution Protocol)
ldp_parameters = {
    "label_space": [0, 16, 32],
    "transport_address": ["192.168.1.1", "10.0.0.1"]
}
