"""
Demonstrates pandoraPlugintools.disco_output: print the accumulated
discovery JSON (summary/info/monitoring_data) to stdout and exit the
process with the configured error level.

disco_output() calls sys.exit(), which terminates the interpreter, so
it is guarded behind __main__ and shown as the last statement of a
plugin's main entry point.
"""

import pandoraPlugintools as ppt

if __name__ == "__main__":
    ppt.set_disco_summary()
    ppt.set_disco_summary_value("hosts_scanned", 10)

    ppt.add_disco_info_value("Discovery scan finished.\n")

    ppt.add_disco_monitoring_data({"host": "192.168.1.10", "status": "up"})

    ppt.set_disco_error_level(0)

    # Prints the JSON output and calls sys.exit(0).
    ppt.disco_output()
