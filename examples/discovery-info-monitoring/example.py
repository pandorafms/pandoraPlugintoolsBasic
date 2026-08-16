"""
Demonstrates pandoraPlugintools.add_disco_info_value,
set_disco_monitoring_data and add_disco_monitoring_data: build up the
"info" and "monitoring_data" sections used by disco_output.
"""

import pandoraPlugintools as ppt

ppt.add_disco_info_value("Discovery scan started.\n")
ppt.add_disco_info_value("Found 3 hosts.\n")

ppt.set_disco_monitoring_data([])
ppt.add_disco_monitoring_data({"host": "192.168.1.10", "status": "up"})
ppt.add_disco_monitoring_data({"host": "192.168.1.11", "status": "down"})

print("Info and monitoring data queued; see discovery-output example for the final JSON.")
