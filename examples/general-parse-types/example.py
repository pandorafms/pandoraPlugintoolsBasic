"""
Demonstrates pandoraPlugintools.parse_int / parse_float / parse_str /
parse_bool: best-effort type conversion that falls back to a safe
default instead of raising.
"""

import pandoraPlugintools as ppt

print(ppt.parse_int("42"))
print(ppt.parse_int("not a number"))

print(ppt.parse_float("3.14"))
print(ppt.parse_float("not a float"))

print(ppt.parse_str(123))

print(ppt.parse_bool(1))
print(ppt.parse_bool(""))
