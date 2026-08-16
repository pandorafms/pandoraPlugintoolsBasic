import pandoraPlugintools as ppt

m = ppt.init_module({"name": "x", "value": "10"})
assert "<data><![CDATA[10]]></data>" in ppt.print_module(m)

ppt.set_monitoring_items([])
ppt.add_monitoring_item({"agent_name": "host1"}, [{"name": "CPU", "type": "generic_data", "data": 30}])
payload = ppt.print_monitoring_payload()
assert '"agent_data"' in payload and '"module_data"' in payload
ppt.set_monitoring_items([])

print("ok")
