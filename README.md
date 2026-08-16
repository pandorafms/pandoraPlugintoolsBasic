# pandoraPlugintoolsBasic

`pandoraPlugintoolsBasic` is a lightweight, dependency-free version of `pandoraPlugintools` for Pandora FMS plugin development.

It is designed as a drop-in replacement for the most commonly used functionality, with a smaller footprint and simpler deployment.

## Install

```bash
pip install pandoraPlugintools-basic
```

## Migration from pandoraPlugintools

If your plugin only uses the basic features included in this package, migrate with:

```bash
pip uninstall pandoraPlugintools
pip install pandoraPlugintools-basic
```

Important:
- This package does not include all features from the full `pandoraPlugintools` package.
- If your current code depends on advanced modules (for example SNMP or encryption helpers), keep using the standard package.

## What is included

The package exports the following modules:

- `general`: General-purpose helper functions for plugin development.
- `threads`: Utilities for running functions in parallel.
- `agents`: Functions to build Pandora FMS agent payloads.
- `modules`: Functions to build Pandora FMS module payloads.
- `transfer`: File transfer and data sending helpers.
- `discovery`: Helpers for Pandora FMS discovery plugins.
- `output`: Output formatting and return helpers.

Reference documentation:
[PluginTools Reference Documentation](https://pandorafms.com/guides/public/books/plugintools)

For a full, runnable example per function, see [docs/examples.md](docs/examples.md).

## Most used functions

The README stays focused on the quick path. For a complete function list and full details, use the reference documentation link above.

| Module | Common functions |
|-------|------------------|
| `general` | `generate_md5`, `safe_input`, `safe_output`, `parse_configuration`, `parse_csv_file`, `translate_macros`, `now` |
| `agents` | `init_agent`, `print_agent`, `get_os` |
| `modules` | `init_module`, `print_module`, `init_log_module`, `print_log_module` |
| `transfer` | `write_xml`, `transfer_xml`, `tentacle_xml` |
| `threads` | `run_threads`, `run_processes`, `set_shared_dict_value`, `get_shared_dict_value` |
| `discovery` | `set_disco_summary`, `add_disco_summary_value`, `add_disco_info_value`, `add_disco_monitoring_data`, `disco_output` |
| `output` | `print_stdout`, `print_stderr`, `print_debug`, `logger` |

## Quick example

```python
import pandoraPlugintools as ppt

# Define agent
server_name = "WIN-SERV"

agent = ppt.init_agent(
    {
        "agent_name": ppt.generate_md5(server_name),
        "agent_alias": server_name,
        "description": "Default Windows server",
    }
)

# Define modules
modules = []
data = 10

modules.append(
    {
        "name": "CPU usage",
        "type": "generic_data",
        "value": data,
        "desc": "Percentage of CPU utilization",
        "unit": "%",
    }
)

# Generate and transfer XML
xml_content = ppt.print_agent(agent, modules)
xml_file = ppt.write_xml(xml_content, agent["agent_name"])

ppt.transfer_xml(
    xml_file,
    transfer_mode="tentacle",
    tentacle_ip="192.168.1.20",
    tentacle_port="41121",
)
```

