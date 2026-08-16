"""
Demonstrates pandoraPlugintools.write_xml: write an agent XML string
to a local .data file, ready to be picked up or transferred.
"""

import os
import tempfile

import pandoraPlugintools as ppt

agent = ppt.init_agent({"agent_name": ppt.generate_md5("WIN-SERV"), "agent_alias": "WIN-SERV"})
xml_content = ppt.print_agent(agent, [])

with tempfile.TemporaryDirectory() as tmp_dir:
    data_file = ppt.write_xml(xml_content, agent["agent_name"], data_dir=tmp_dir)

    print(data_file)
    print(os.path.exists(data_file))
