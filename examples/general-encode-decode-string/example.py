"""
Demonstrates pandoraPlugintools.encode_string / decode_string:
base64 encode and decode a string.
"""

import pandoraPlugintools as ppt

encoded = ppt.encode_string("Hello Pandora FMS")
print(encoded)

decoded = ppt.decode_string(encoded)
print(decoded)
