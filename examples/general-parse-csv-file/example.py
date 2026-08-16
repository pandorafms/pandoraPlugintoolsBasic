"""
Demonstrates pandoraPlugintools.parse_csv_file: read a CSV-like file
into a list of value lists, skipping short lines.
"""

import os
import tempfile

import pandoraPlugintools as ppt

csv_content = "\n".join(
    [
        "# name;value;unit",
        "CPU;10;%",
        "Memory;55;%",
    ]
)

with tempfile.TemporaryDirectory() as tmp_dir:
    csv_path = os.path.join(tmp_dir, "data.csv")
    with open(csv_path, "w") as f:
        f.write(csv_content)

    rows = ppt.parse_csv_file(
        file=csv_path,
        separator=";",
        count_parameters=3,
        print_errors=True,
    )

    print(rows)
