INTERFACE_CONFIG = """
interface {{ interface }}
 ip address {{ ip }} {{ mask }}
{% if shutdown %}
 shutdown
{% else %}
 no shutdown
{% endif %}
exit
"""

STATIC_ROUTE = """
ip route {{ network }} {{ mask }} {{ next_hop }}
"""

DHCP_CONFIG = """
ip dhcp excluded-address {{ excluded_start }} {{ excluded_end }}
ip dhcp pool {{ pool_name }}
 network {{ network }} {{ mask }}
 default-router {{ default_router }}
 dns-server {{ dns_server }}
"""

TEMPLATES = {
    "interface_config": INTERFACE_CONFIG,
    "static_route": STATIC_ROUTE,
    "dhcp_config": DHCP_CONFIG,
}