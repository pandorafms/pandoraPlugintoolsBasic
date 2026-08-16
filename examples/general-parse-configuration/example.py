"""
Demonstrates pandoraPlugintools.parse_configuration: read a simple
"key value" configuration file into a dict, applying defaults for
missing keys.
"""

import os
import tempfile

import pandoraPlugintools as ppt

config_content = "\n".join(
    [
        "# Example plugin config",
        "server_ip 192.168.1.20",
        "interval 300",
    ]
)

with tempfile.TemporaryDirectory() as tmp_dir:
    config_path = os.path.join(tmp_dir, "plugin.conf")
    with open(config_path, "w") as f:
        f.write(config_content)

    config = ppt.parse_configuration(
        file=config_path,
        separator=" ",
        default_values={"timeout": "10"},
    )

    print(config)
