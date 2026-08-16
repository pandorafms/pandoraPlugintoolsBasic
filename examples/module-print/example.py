"""
Demonstrates pandoraPlugintools.print_module: render a single module
(and a module with a datalist) as XML.

Note: since init_module's template always includes a "data" key,
print_module copies "data" over "value" when rendering -- so set
"data" (not "value") to control the module's reported value.
"""

import pandoraPlugintools as ppt

module = ppt.init_module(
    {
        "name": "CPU usage",
        "type": "generic_data",
        "data": 10,
        "desc": "Percentage of CPU utilization",
        "unit": "%",
    }
)

print(ppt.print_module(module))

# A module with a list of timestamped values (datalist).
datalist_module = ppt.init_module(
    {
        "name": "CPU usage history",
        "type": "generic_data",
        "data": [
            {"value": 10, "timestamp": "2024-01-01 00:00:00"},
            {"value": 15, "timestamp": "2024-01-01 00:05:00"},
        ],
    }
)

print(ppt.print_module(datalist_module))
