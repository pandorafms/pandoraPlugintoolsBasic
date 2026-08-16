"""
Demonstrates pandoraPlugintools.add_monitoring_item and
print_monitoring_payload: build the JSON array accepted by the
'/monitoring' API endpoint from plain agent_data/module_data dicts,
the way real discovery plugins build it by hand.
"""

import pandoraPlugintools as ppt

ppt.set_monitoring_items([])

agent_data = {
    "agent_name": "nginx-01",
    "os": "Linux",
    "interval": 300,
}
module_data = [
    {"name": "nginx_status", "type": "generic_proc", "data": 1},
    {"name": "active_connections", "type": "generic_data", "data": 42},
]

ppt.add_monitoring_item(agent_data, module_data)

ppt.print_monitoring_payload(print_flag=True)
