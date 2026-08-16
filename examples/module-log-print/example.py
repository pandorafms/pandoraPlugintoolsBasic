"""
Demonstrates pandoraPlugintools.print_log_module: render a log module
as XML, optionally with an encoding attribute.
"""

import pandoraPlugintools as ppt

log_module = ppt.init_log_module({"source": "syslog", "value": "example log line"})

print(ppt.print_log_module(log_module))
print(ppt.print_log_module(log_module, encoding="base64"))
