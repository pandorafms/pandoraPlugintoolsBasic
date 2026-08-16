"""
Demonstrates pandoraPlugintools.safe_input / safe_output: convert
between raw text and its HTML-entity-escaped representation.
"""

import pandoraPlugintools as ppt

raw_text = "5 < 10 & 10 > 5"

escaped = ppt.safe_input(raw_text)
print(escaped)

restored = ppt.safe_output(escaped)
print(restored)

assert restored == raw_text
