"""
Demonstrates pandoraPlugintools.init_log_module: build a log module
data dict populated with defaults, overridden with custom values.
"""

import pandoraPlugintools as ppt

log_module = ppt.init_log_module({"source": "syslog", "value": "example log line"})

print(log_module)
