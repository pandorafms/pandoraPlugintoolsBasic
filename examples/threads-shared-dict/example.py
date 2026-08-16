"""
Demonstrates pandoraPlugintools.set_shared_dict_value /
add_shared_dict_value / get_shared_dict_value: a process/thread-safe
shared dict used to accumulate results across parallel workers.
"""

import pandoraPlugintools as ppt

ppt.set_shared_dict_value("errors", 0)
ppt.add_shared_dict_value("errors", 1)
ppt.add_shared_dict_value("errors", 1)

print(ppt.get_shared_dict_value("errors"))
print(ppt.get_shared_dict_value("missing_key"))
