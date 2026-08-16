"""
Demonstrates pandoraPlugintools.set_disco_summary / set_disco_summary_value
/ add_disco_summary_value: build up the "summary" section used by
disco_output.

Note: set_disco_summary() always resets the internal summary to an
empty dict (its "data" argument is currently unused by the library),
so it is only useful to clear previous state before adding values.
"""

import pandoraPlugintools as ppt

ppt.set_disco_summary()

ppt.set_disco_summary_value("hosts_scanned", 10)
ppt.add_disco_summary_value("hosts_scanned", 5)

print("Summary values queued (hosts_scanned=15); see discovery-output example for the final JSON.")
