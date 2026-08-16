"""
Demonstrates pandoraPlugintools.init_agent: build an agent configuration
dict populated with sane defaults, overridden with custom values.
"""

import pandoraPlugintools as ppt

agent = ppt.init_agent(
    {
        "agent_name": ppt.generate_md5("WIN-SERV"),
        "agent_alias": "WIN-SERV",
        "description": "Default Windows server",
    }
)

print(agent)
