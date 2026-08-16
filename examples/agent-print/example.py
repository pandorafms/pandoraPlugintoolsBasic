"""
Demonstrates pandoraPlugintools.print_agent: render an agent plus its
modules and log modules as a Pandora FMS agent XML string.

Note: modules built with init_module() must set "data" (not "value")
to control the rendered value -- see the module-init/module-print
examples for details.
"""

import pandoraPlugintools as ppt

agent = ppt.init_agent(
    {
        "agent_name": ppt.generate_md5("WIN-SERV"),
        "agent_alias": "WIN-SERV",
        "description": "Default Windows server",
    }
)

modules = [
    ppt.init_module(
        {
            "name": "CPU usage",
            "type": "generic_data",
            "data": 10,
            "desc": "Percentage of CPU utilization",
            "unit": "%",
        }
    )
]

log_modules = [ppt.init_log_module({"source": "syslog", "value": "example log line"})]

xml_content = ppt.print_agent(agent, modules, log_modules)

print(xml_content)
