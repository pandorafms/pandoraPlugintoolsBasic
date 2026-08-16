"""
Demonstrates pandoraPlugintools.print_stdout / print_stderr /
print_debug: basic output helpers used across the library.
"""

import pandoraPlugintools as ppt

ppt.print_stdout("This goes to stdout")
ppt.print_stderr("This goes to stderr")

ppt.print_debug({"cpu": 10, "memory": 55, "tags": ["prod", "web"]})
