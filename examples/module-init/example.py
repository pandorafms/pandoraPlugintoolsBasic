"""
Demonstrates pandoraPlugintools.init_module: build a module data dict
populated with defaults, overridden with custom values.

Note: init_module's template has both "data" and "value" keys. When the
module is later rendered with print_module, "data" (if present) is
copied over "value", so set "data" -- not "value" -- to control the
module's reported value.
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

print(module)
