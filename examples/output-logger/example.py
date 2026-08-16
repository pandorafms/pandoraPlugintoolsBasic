"""
Demonstrates pandoraPlugintools.logger: append timestamped lines to a
log file.
"""

import os
import tempfile

import pandoraPlugintools as ppt

with tempfile.TemporaryDirectory() as tmp_dir:
    log_file = os.path.join(tmp_dir, "plugin.log")

    ppt.logger(log_file, "Plugin started", log_level="INFO")
    ppt.logger(log_file, "Something looked off", log_level="WARNING")

    with open(log_file) as f:
        print(f.read())
