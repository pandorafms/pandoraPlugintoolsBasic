# Examples

The repository includes runnable example scripts under `examples/`.

## General

- `examples/general-generate-md5/example.py` — `generate_md5` — hash a string to its MD5 hex digest.
- `examples/general-now/example.py` — `now` — current time as a formatted string or Unix timestamp.
- `examples/general-safe-input-output/example.py` — `safe_input` / `safe_output` — convert between raw text and HTML-entity-escaped text.
- `examples/general-translate-macros/example.py` — `translate_macros` — replace macro placeholders in a string.
- `examples/general-parse-configuration/example.py` — `parse_configuration` — parse a `key value` config file into a dict.
- `examples/general-parse-csv-file/example.py` — `parse_csv_file` — parse a separator-delimited file into a list of rows.
- `examples/general-parse-types/example.py` — `parse_int` / `parse_float` / `parse_str` / `parse_bool` — best-effort type conversion with safe fallbacks.
- `examples/general-encode-decode-string/example.py` — `encode_string` / `decode_string` — base64 encode/decode a string.
- `examples/general-dict-key-value/example.py` — `set_dict_key_value` / `get_dict_key_value` — safe dict key assignment/lookup.

## Agents

- `examples/agent-init/example.py` — `init_agent` — build an agent configuration dict with defaults.
- `examples/agent-print/example.py` — `print_agent` — render an agent plus modules/log modules as XML.
- `examples/agent-get-os/example.py` — `get_os` — detect the current OS family.
- `examples/agent-class-basic/example.py` — `Agent` — object-oriented wrapper for managing an agent's modules.

## Modules

- `examples/module-init/example.py` — `init_module` — build a module data dict with defaults.
- `examples/module-print/example.py` — `print_module` — render a module (including a datalist module) as XML.
- `examples/module-log-init/example.py` — `init_log_module` — build a log module data dict with defaults.
- `examples/module-log-print/example.py` — `print_log_module` — render a log module as XML.
- `examples/module-img-print/example.py` — `print_img_module` — render an image module as XML with a base64 data URI.

## Threads

- `examples/threads-run-threads/example.py` — `run_threads` — run a function over a list of items using a thread pool.
- `examples/threads-shared-dict/example.py` — `set_shared_dict_value` / `add_shared_dict_value` / `get_shared_dict_value` — thread/process-safe shared dict.
- `examples/threads-run-processes/example.py` — `run_processes` — run a function over a list of items using a process pool.

## Transfer

- `examples/transfer-write-xml/example.py` — `write_xml` — write agent XML to a local `.data` file.
- `examples/transfer-transfer-xml/example.py` — `transfer_xml` — deliver a `.data` file locally or via Tentacle.

## Discovery

- `examples/discovery-summary/example.py` — `set_disco_summary` / `set_disco_summary_value` / `add_disco_summary_value` — build the discovery "summary" section.
- `examples/discovery-info-monitoring/example.py` — `add_disco_info_value` / `set_disco_monitoring_data` / `add_disco_monitoring_data` — build the "info" and "monitoring_data" sections.
- `examples/discovery-output/example.py` — `disco_output` — print the discovery JSON and exit the process.

## Monitoring API

- `examples/monitoring-build-payload/example.py` — `add_monitoring_item` / `print_monitoring_payload` — build the JSON array accepted by the console API v2 `/monitoring` endpoint.
- `examples/monitoring-send-payload/example.py` — same payload, then send it to `/monitoring` with the third-party `requests` library.

## Output

- `examples/output-print-functions/example.py` — `print_stdout` / `print_stderr` / `print_debug` — basic output helpers.
- `examples/output-logger/example.py` — `logger` — append timestamped lines to a log file.

## Notes

- Run any example from the repository root with:

  ```bash
  PYTHONPATH=. python3 examples/<folder>/example.py
  ```

  `PYTHONPATH=.` is required because the package is imported as `pandoraPlugintools` from the local source tree, without installing it first.
- `examples/discovery-output/example.py` calls `sys.exit()` (via `disco_output`), so it terminates the process after printing its JSON output — this matches how a real discovery plugin ends.
- `examples/transfer-transfer-xml/example.py` uses local transfer mode so it runs without external dependencies. Tentacle mode requires a reachable Tentacle server and the `tentacle_client` binary on `PATH`; see the comment in that example for the equivalent call.
- `examples/threads-run-processes/example.py` requires its worker function to be defined at module level (not a lambda or closure) since `multiprocessing` needs to pickle it.
- Modules built with `init_module()` (directly, via the `Agent` class, or via `print_agent`) always include both a `data` and a `value` key. Whichever one you pass explicitly is mirrored onto the other, so the same module dict renders correctly as XML (`print_module`/`print_agent`) and works as-is as `module_data` for the monitoring API JSON payload. Modules built as plain dicts without going through `init_module()` (as in `examples/module-img-print/example.py`) do not get this mirroring and should set the key the target format expects directly.
- `requests` is only used inside `examples/monitoring-send-payload/example.py` and is not a dependency of `pandoraPlugintools` itself. That example is a dry run (it only prints the request it would make) unless the `PANDORA_MONITORING_URL` environment variable is set.
