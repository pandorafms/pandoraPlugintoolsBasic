"""
Demonstrates pandoraPlugintools.transfer_xml: deliver a generated
.data file either to a local Pandora FMS data_in directory or, in
Tentacle mode, to a remote Tentacle server.

This example uses "local" mode so it runs without a real Tentacle
server. To use Tentacle mode instead, call:

    ppt.transfer_xml(
        data_file,
        transfer_mode="tentacle",
        tentacle_ip="192.168.1.20",
        tentacle_port=41121,
    )

which requires a reachable Tentacle server and the tentacle_client
binary available on PATH.
"""

import os
import tempfile

import pandoraPlugintools as ppt

agent = ppt.init_agent({"agent_name": ppt.generate_md5("WIN-SERV"), "agent_alias": "WIN-SERV"})
xml_content = ppt.print_agent(agent, [])

with tempfile.TemporaryDirectory() as staging_dir, tempfile.TemporaryDirectory() as data_in_dir:
    data_file = ppt.write_xml(xml_content, agent["agent_name"], data_dir=staging_dir)

    ppt.transfer_xml(data_file, transfer_mode="local", data_dir=data_in_dir)

    delivered_files = os.listdir(data_in_dir)
    print(delivered_files)
