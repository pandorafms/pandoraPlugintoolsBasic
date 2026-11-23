####
# Post-transform block engine for Discovery tasks (ticket #22040).
#
# Task operators describe ordered transform rules as plain-text blocks and the
# engine merges whitelisted module configuration fields into the collected
# agent/module structure BEFORE it is serialized to its final format, so the
# same rules work for the native JSON path and the tentacle XML path.
#
# Block grammar (one rule per block):
#
#     transform_begin
#     transform_name       <optional label>
#     match_module         <regex against the module name>
#     match_extra_data     <regex against the module extra_data>
#     set_<field>          <typed value from the whitelist>
#     transform_end
#
# Semantics:
#   - Comments (#) and blank lines are ignored everywhere.
#   - Match keys inside a block are AND-ed; a rule must have at least one.
#   - Rules apply in order; for each field the last matching rule wins.
#   - 'name', 'type', 'data', 'value', 'extra_data', 'timestamp' and 'status'
#     are protected: they define module identity and the collected value.
#   - Threshold ranges are half-open [min, max); max_warning=0 / max_critical=0
#     mean "no upper limit", not the literal zero.
#   - Unknown keys, invalid regexes and mistyped values are reported as rule
#     errors naming the block and the key. The tolerant API skips the
#     offending rule and keeps the rest, so one bad rule never throws away
#     the whole monitoring run; the strict API raises instead.
#########################################################################################

import re

####
# Whitelist: set_<field> key -> value type.
# Mirrors the module fields that init_module() templates and print_module()
# serializes, i.e. the vocabulary the Discovery ingestion already accepts.
#########################################################################################

WHITELIST = {
    # Numeric thresholds.
    "min_warning": "number",
    "max_warning": "number",
    "min_critical": "number",
    "max_critical": "number",
    "min_warning_forced": "number",
    "max_warning_forced": "number",
    "min_critical_forced": "number",
    "max_critical_forced": "number",
    "min": "number",
    "max": "number",
    "post_process": "number",
    # String thresholds.
    "str_warning": "str",
    "str_critical": "str",
    "str_warning_forced": "str",
    "str_critical_forced": "str",
    # Inverse / on-off flags (0 or 1).
    "critical_inverse": "int01",
    "warning_inverse": "int01",
    "quiet": "int01",
    "disabled": "int01",
    "each_ff": "int01",
    # Flip-flop settings, interval and cron.
    "min_ff_event": "int",
    "min_ff_event_normal": "int",
    "min_ff_event_warning": "int",
    "min_ff_event_critical": "int",
    "ff_type": "int",
    "ff_timeout": "int",
    "module_ff_interval": "int",
    "interval": "int",
    "crontab": "str",
    # Grouping, identification and instructions.
    "tags": "str",
    "module_group": "str",
    "module_parent": "str",
    "module_parent_unlink": "str",
    "custom_id": "str",
    "description": "str",
    "critical_instructions": "str",
    "warning_instructions": "str",
    "unknown_instructions": "str",
    # Alert templates: appended to the module "alert" list.
    "alert_template": "alert",
}

####
# Fields a rule can never write: module identity and the collected value.
#########################################################################################

PROTECTED_FIELDS = (
    "name",
    "type",
    "data",
    "value",
    "extra_data",
    "timestamp",
    "status",
)

####
# Keys allowed inside a transform block, besides set_<whitelist field>.
#########################################################################################

MATCH_KEYS = {
    "match_module": "module",
    "match_extra_data": "extra_data",
}

####
# Raised when transform blocks cannot be parsed or validated.
# The message always names the block (and line when known) so the task owner
# can fix the rule file without reading engine code.
#########################################################################################

class TransformParseError(ValueError):
    """Transform blocks are malformed or contain invalid values."""


####
# Internal: strip the invisible characters the IoT filter files also strip.
#########################################################################################

def _clean_line(line: str) -> str:
    return re.sub(r'[\u200b\ufeff]', '', line).strip()


####
# Internal: key/value grammar of a line inside a block.
#########################################################################################

_LINE_RE = re.compile(r'^([a-z_][a-z0-9_]*)\s+(.+)$')


####
# Internal: coerce a raw block value to the type the whitelist declares.
#########################################################################################

def _coerce_value(field: str, raw: str, block_no: int, lineno: int):
    kind = WHITELIST[field]
    where = "transform block %d, line %d" % (block_no, lineno)

    if kind == "number":
        try:
            number = float(raw)
        except ValueError:
            raise TransformParseError(
                "%s: set_%s expects a number, got %r" % (where, field, raw)
            )
        return int(number) if number.is_integer() else number

    if kind in ("int", "int01"):
        try:
            number = int(raw)
        except ValueError:
            raise TransformParseError(
                "%s: set_%s expects an integer, got %r" % (where, field, raw)
            )
        if kind == "int01" and number not in (0, 1):
            raise TransformParseError(
                "%s: set_%s expects 0 or 1, got %r" % (where, field, raw)
            )
        return number

    return raw


####
# Tolerant parse core: parse every block, skipping the invalid RULES while
# keeping the valid ones, and collecting one error string per problem, each
# naming its block and line. Rule granularity: one bad key invalidates its
# whole rule (block), because applying half of an intended configuration is
# worse than skipping it.
#########################################################################################

def _parse_blocks_tolerant(rules_text: str):
    rules = []
    errors = []
    current = None
    current_errors = None
    block_no = 0
    lineno = 0

    for raw_line in rules_text.splitlines():
        lineno += 1
        line = _clean_line(raw_line)

        if not line or line.startswith("#"):
            continue

        if line == "transform_begin":
            if current is not None:
                errors.append(
                    "transform block %d, line %d: missing transform_end "
                    "before a new transform_begin; rule skipped"
                    % (block_no, lineno)
                )
            block_no += 1
            current = {"name": "", "match": {}, "set": {}}
            current_errors = []
            continue

        if line == "transform_end":
            if current is None:
                errors.append(
                    "line %d: transform_end without transform_begin" % lineno
                )
                continue

            if not current["match"]:
                current_errors.append(
                    "transform block %d: rule has no match_module or "
                    "match_extra_data key; rule skipped" % block_no
                )

            for key, pattern in current["match"].items():
                try:
                    re.compile(pattern)
                except re.error as error:
                    current_errors.append(
                        "transform block %d: invalid regex in match key %r: "
                        "%s; rule skipped" % (block_no, key, error)
                    )

            if current_errors:
                errors.extend(current_errors)
            else:
                rules.append(current)

            current = None
            current_errors = None
            continue

        if current is None:
            errors.append(
                "line %d: content outside a transform block: %r"
                % (lineno, line)
            )
            continue

        parsed = _LINE_RE.match(line)
        if parsed is None:
            current_errors.append(
                "transform block %d, line %d: cannot parse line: %r; rule "
                "skipped" % (block_no, lineno, line)
            )
            continue

        key = parsed.group(1)
        value = parsed.group(2).strip()

        if key == "transform_name":
            current["name"] = value
        elif key in MATCH_KEYS:
            current["match"][MATCH_KEYS[key]] = value
        elif key.startswith("set_"):
            field = key[4:]
            if field in PROTECTED_FIELDS:
                current_errors.append(
                    "transform block %d, line %d: field %r is protected and "
                    "cannot be set; rule skipped" % (block_no, lineno, field)
                )
            elif field not in WHITELIST:
                current_errors.append(
                    "transform block %d, line %d: unknown set field %r (not "
                    "in the whitelist); rule skipped" % (block_no, lineno, field)
                )
            else:
                try:
                    current["set"][field] = _coerce_value(
                        field, value, block_no, lineno
                    )
                except TransformParseError as error:
                    current_errors.append("%s; rule skipped" % error)
        else:
            current_errors.append(
                "transform block %d, line %d: unknown key %r; rule skipped"
                % (block_no, lineno, key)
            )

    if current is not None:
        errors.append(
            "transform block %d: missing transform_end at end of input; rule "
            "skipped" % block_no
        )

    return rules, errors


####
# Parse transform blocks into an ordered list of rule dicts:
#   {"name": <label>, "match": {"module": <regex>, "extra_data": <regex>},
#    "set": {<field>: <typed value>}}
#
# STRICT variant: raises TransformParseError on the first invalid rule.
#########################################################################################

def parse_transform_blocks(rules_text: str) -> list:
    rules, errors = _parse_blocks_tolerant(rules_text)

    if errors:
        raise TransformParseError("\n".join(errors))

    return rules


####
# Tolerant variant for plugins: one bad rule never throws away the whole
# monitoring run. Returns (rules, errors); valid rules apply normally and
# each error names its block and line so the task can report it (for example
# through add_disco_info_value plus an error level) while continuing.
#########################################################################################

def parse_transform_blocks_tolerant(rules_text: str) -> tuple:
    return _parse_blocks_tolerant(rules_text)


####
# Internal: does one rule match one module?
# Match uses re.search semantics (substring); anchor patterns with ^...$ to
# require a full match.
#########################################################################################

def _rule_matches(module: dict, rule: dict) -> bool:
    match = rule["match"]

    if "module" in match:
        if not re.search(match["module"], str(module.get("name") or "")):
            return False

    if "extra_data" in match:
        if not re.search(match["extra_data"], str(module.get("extra_data") or "")):
            return False

    return True


####
# Internal: merge one rule's fields into one module. Never touches the
# protected identity fields: 'set_' keys for them do not parse.
#########################################################################################

def _apply_rule(module: dict, rule: dict) -> bool:
    touched = False

    for field, value in rule["set"].items():
        if WHITELIST.get(field) == "alert":
            alerts = module.get("alert")
            if not isinstance(alerts, list):
                alerts = []
                module["alert"] = alerts
            alerts.append(value)
        else:
            module[field] = value
        touched = True

    return touched


####
# Apply post-transform rules over collected monitoring data, in place,
# BEFORE serializing it to its final format.
#
# Args:
#     data (list): either the monitoring items list
#         ([{"agent_data": {...}, "module_data": [module dicts]}]) or a plain
#         list of module dicts (the XML path, before print_agent()).
#     rules (list | str): parsed rules from parse_transform_blocks() or the
#         raw block text (parsed here, so errors fail the task before output).
#
# Returns:
#     int: number of modules that received at least one field.
#########################################################################################

def apply_post_transforms(data: list, rules) -> int:
    if isinstance(rules, str):
        rules = parse_transform_blocks(rules)

    changed = 0

    for entry in data:
        if isinstance(entry, dict) and isinstance(entry.get("module_data"), list):
            modules = entry["module_data"]
        else:
            modules = [entry]

        for module in modules:
            if not isinstance(module, dict):
                continue

            touched = False
            for rule in rules:
                if _rule_matches(module, rule) and _apply_rule(module, rule):
                    touched = True

            if touched:
                changed += 1

    return changed
