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
- `monitoring`: Helpers to accumulate and emit `/monitoring` API payloads.
- `output`: Output formatting and return helpers.
- `post_transforms`: Post-transform block engine for Discovery tasks (regex rules that merge whitelisted module fields before serialization).

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
| `monitoring` | `set_monitoring_items`, `add_monitoring_item`, `get_monitoring_items`, `print_monitoring_payload` |
| `post_transforms` | `parse_transform_blocks`, `apply_post_transforms`, `TransformParseError` |
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

## Post-transform blocks for Discovery tasks

Discovery plugins can let task operators enrich modules without touching plugin
code. Operators write ordered rule blocks in plain text; the plugin applies
them over the collected agent/module structure right before serializing it, so
the same rules work for the native JSON path and the tentacle XML path.

```text
transform_begin
transform_name       cpu thresholds
match_module         .*cpu_percent
match_extra_data     .*:metric:cpu
set_min_warning      80
set_max_critical     0
set_module_group     Rendimiento
set_tags             infra:cpu
transform_end
```

Semantics:

- `match_module` and `match_extra_data` are regexes (substring match; use
  `^...$` for full match) AND-ed inside a block; a rule needs at least one.
- Rules apply in order; for each field the last matching rule wins.
- `set_<field>` accepts exactly the module fields the Discovery ingestion
  already supports (thresholds, `str_*`, `tags`, `module_group`,
  `alert_template`, FF settings, `custom_id`, ...). Unknown fields are errors.
- `set_tags` holds a comma-separated list (`set_tags infra,ops`), the same
  convention as the agent's `module_tags`: the whole string travels in one
  field and the server splits it.
- `name`, `type`, `data`, `value`, `extra_data`, `timestamp` and `status` are
  protected: a rule cannot change module identity or the collected value.
- Threshold ranges are half-open `[min, max)`; `max_warning=0` and
  `max_critical=0` mean "no upper limit", not the literal zero.
- Invalid regexes, unknown keys and mistyped values are reported with the
  block and key that caused them: the tolerant API
  (`parse_transform_blocks_tolerant`) skips the offending rule and keeps the
  rest, so one bad rule never throws away the monitoring run; the strict API
  (`parse_transform_blocks`) raises `TransformParseError` instead.

```python
import pandoraPlugintools as ppt

rules_text = open("post_transforms.conf").read()

# Tolerant parse: bad rules are skipped and reported; good rules apply.
rules, errors = ppt.parse_transform_blocks_tolerant(rules_text)
if errors:
    ppt.set_disco_error_level(1)
    for error in errors:
        ppt.add_disco_info_value("post-transforms: %s\n" % error)
        ppt.print_stderr("post-transforms: %s\n" % error)

# JSON path: over the accumulated monitoring items.
items = ppt.get_monitoring_items()
ppt.apply_post_transforms(items, rules)
payload = ppt.print_monitoring_payload()

# XML path: over the module list, before print_agent().
ppt.apply_post_transforms(modules, rules)
xml_content = ppt.print_agent(agent, modules)
```

The errors are reported in the discovery JSON (`info` plus a non-zero error
level) and on stderr, so manual runs show them immediately; the monitoring
itself is never stopped by a bad rule.

