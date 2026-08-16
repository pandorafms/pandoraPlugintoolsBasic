"""
Demonstrates pandoraPlugintools.translate_macros: replace macro
placeholders in a string using a dict of macro name -> value.
"""

import pandoraPlugintools as ppt

macros = {
    "_host_": "srv-01",
    "_port_": "8080",
}

result = ppt.translate_macros(macros, "Connecting to _host_:_port_")

print(result)
