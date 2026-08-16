"""
Demonstrates pandoraPlugintools.now: get the current time as a
formatted string or as a Unix timestamp.
"""

import pandoraPlugintools as ppt

print(ppt.now())
print(ppt.now(utimestamp=True))
