"""
Demonstrates pandoraPlugintools.set_dict_key_value / get_dict_key_value:
helper functions to safely assign/read a dict key (trimming whitespace
in the key name).
"""

import pandoraPlugintools as ppt

data = {}

ppt.set_dict_key_value(data, "  server_ip ", "192.168.1.20")

print(data)
print(ppt.get_dict_key_value(data, "server_ip"))
print(ppt.get_dict_key_value(data, "missing_key"))
