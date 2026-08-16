"""
Demonstrates the pandoraPlugintools.Agent class: an object-oriented
wrapper around init_agent/print_agent that manages modules and log
modules internally.

Note: modules go through init_module() internally, so set "data" (not
"value") to control the rendered value -- see the module-init/module-print
examples for details.
"""

import pandoraPlugintools as ppt

agent = ppt.Agent(
    config={
        "agent_name": ppt.generate_md5("WIN-SERV"),
        "agent_alias": "WIN-SERV",
        "description": "Default Windows server",
    },
    modules_def=[
        {
            "name": "CPU usage",
            "type": "generic_data",
            "data": 10,
            "desc": "Percentage of CPU utilization",
            "unit": "%",
        }
    ],
    log_modules_def=[{"source": "syslog", "value": "example log line"}],
)

# Modules can be inspected, updated or removed by name.
print(agent.get_module("CPU usage"))

agent.update_module("CPU usage", {"data": 42})
print(agent.get_module("CPU usage"))

# Render the final XML for this agent.
print(agent.print_xml())
