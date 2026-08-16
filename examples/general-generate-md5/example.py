"""
Demonstrates pandoraPlugintools.generate_md5: hash a string to its
MD5 hex digest (commonly used to build agent_name values).
"""

import pandoraPlugintools as ppt

print(ppt.generate_md5("WIN-SERV"))
