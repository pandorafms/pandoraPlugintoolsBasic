import pandoraPlugintools as ppt

m = ppt.init_module({"name": "x", "value": "10"})
assert "<data><![CDATA[10]]></data>" in ppt.print_module(m)

print("ok")