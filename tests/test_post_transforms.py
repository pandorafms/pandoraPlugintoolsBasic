# Post-transform block engine tests (ticket #22040).
# Run with: python3 tests/test_post_transforms.py
# Follows the plain assert-script convention of tests/test_basic.py.

# Python 3.14 defaults to forkserver; threads.py creates a Manager() at import
# time, which under forkserver re-imports this script and dies. Use the
# classic fork start method before importing the package.
import multiprocessing
multiprocessing.set_start_method("fork", force=True)

import pandoraPlugintools as ppt

VALID_RULES = """
# Thresholds for CPU-like metrics.
transform_begin
transform_name       cpu thresholds
match_module         .*cpu_percent
match_extra_data     .*:metric:cpu
set_min_warning      80
set_max_critical     0
set_module_group     Rendimiento
set_tags             infra:cpu
transform_end

transform_begin
transform_name       disk usage
match_module         .*disk_usage.*percent
set_min_warning      0.5
set_str_warning      high usage
transform_end
"""

# --- Parsing ---------------------------------------------------------------

rules = ppt.parse_transform_blocks(VALID_RULES)
assert len(rules) == 2, "expected two rules, got %d" % len(rules)

assert rules[0]["name"] == "cpu thresholds"
assert rules[0]["match"]["module"] == ".*cpu_percent"
assert rules[0]["match"]["extra_data"] == ".*:metric:cpu"
assert rules[0]["set"]["min_warning"] == 80, "int coercion failed"
assert rules[0]["set"]["max_critical"] == 0, "int coercion of 0 failed"
assert rules[0]["set"]["module_group"] == "Rendimiento"
assert rules[0]["set"]["tags"] == "infra:cpu"

assert rules[1]["set"]["min_warning"] == 0.5, "float coercion failed"
assert rules[1]["set"]["str_warning"] == "high usage"

# Strict grammar: unknown set key is an error naming block and key.
try:
    ppt.parse_transform_blocks(
        "transform_begin\nmatch_module a\nset_min_warnig 80\ntransform_end\n"
    )
    raise AssertionError("unknown key accepted")
except ppt.TransformParseError as e:
    assert "block 1" in str(e) and "min_warnig" in str(e), str(e)

# Strict grammar: unknown match key is an error.
try:
    ppt.parse_transform_blocks(
        "transform_begin\nmatch_modul a\nset_min_warning 1\ntransform_end\n"
    )
    raise AssertionError("unknown match key accepted")
except ppt.TransformParseError:
    pass

# Strict grammar: garbage line inside a block is an error.
try:
    ppt.parse_transform_blocks("transform_begin\nmatch_module a\nrandom junk\ntransform_end\n")
    raise AssertionError("garbage line accepted")
except ppt.TransformParseError:
    pass

# Strict grammar: non-empty non-comment line outside a block is an error.
try:
    ppt.parse_transform_blocks("random junk outside\ntransform_begin\nmatch_module a\ntransform_end\n")
    raise AssertionError("junk outside blocks accepted")
except ppt.TransformParseError:
    pass

# Unterminated block is an error.
try:
    ppt.parse_transform_blocks("transform_begin\nmatch_module a\nset_min_warning 1\n")
    raise AssertionError("unterminated block accepted")
except ppt.TransformParseError as e:
    assert "block 1" in str(e), str(e)

# Strict API: nested begin reports the skipped rule.
try:
    ppt.parse_transform_blocks("transform_begin\nmatch_module a\ntransform_begin\ntransform_end")
    raise AssertionError("nested begin accepted")
except ppt.TransformParseError as e:
    assert "missing transform_end before a new transform_begin" in str(e), str(e)

# Block without any match key is an error.
try:
    ppt.parse_transform_blocks("transform_begin\nset_min_warning 1\ntransform_end\n")
    raise AssertionError("match-less rule accepted")
except ppt.TransformParseError:
    pass

# Invalid regex is an error naming the block.
try:
    ppt.parse_transform_blocks("transform_begin\nmatch_module ([unclosed\nset_min_warning 1\ntransform_end\n")
    raise AssertionError("invalid regex accepted")
except ppt.TransformParseError as e:
    assert "block 1" in str(e), str(e)

# Non-numeric value for a numeric field is an error.
try:
    ppt.parse_transform_blocks("transform_begin\nmatch_module a\nset_min_warning abc\ntransform_end\n")
    raise AssertionError("non-numeric threshold accepted")
except ppt.TransformParseError:
    pass

# Protected fields are not writable.
for protected in ("name", "type", "data", "value", "extra_data", "timestamp", "status"):
    try:
        ppt.parse_transform_blocks(
            "transform_begin\nmatch_module a\nset_%s x\ntransform_end\n" % protected
        )
        raise AssertionError("protected field %s accepted" % protected)
    except ppt.TransformParseError:
        pass

# --- Apply over monitoring items (native JSON path) -----------------------

items = [
    {
        "agent_data": {"agent_name": "host_1"},
        "module_data": [
            {
                "name": "host_1 cpu_percent",
                "type": "generic_data",
                "data": 55,
                "extra_data": "nginx:metric:cpu",
            },
            {
                "name": "host_1 disk_usage_raw",
                "type": "generic_data",
                "data": 3,
            },
        ],
    }
]

# Convenience: raw block text is accepted and parsed by apply itself.
count = ppt.apply_post_transforms(items, VALID_RULES)
assert count == 1, "expected exactly one module matched, got %d" % count

matched = items[0]["module_data"][0]
assert matched["min_warning"] == 80
assert matched["max_critical"] == 0
assert matched["module_group"] == "Rendimiento"
assert matched["tags"] == "infra:cpu"

unmatched = items[0]["module_data"][1]
assert "min_warning" not in unmatched, "unmatched module was modified"
assert "max_critical" not in unmatched

# Field-level last-match-wins: a later block overrides only its own fields.
layered = """
transform_begin
match_module .*cpu
set_min_warning 10
set_module_group Base
transform_end

transform_begin
match_module .*cpu
set_min_warning 20
transform_end
"""
items2 = [
    {
        "agent_data": {"agent_name": "h2"},
        "module_data": [{"name": "h2 cpu", "type": "generic_data", "data": 1}],
    }
]
ppt.apply_post_transforms(items2, layered)
mod = items2[0]["module_data"][0]
assert mod["min_warning"] == 20, "last-match-wins failed"
assert mod["module_group"] == "Base", "field from earlier block lost"

# AND semantics: both match keys must match.
and_rules = """
transform_begin
match_module .*cpu_percent
match_extra_data .*:metric:cpu
set_min_warning 99
transform_end
"""
items3 = [
    {
        "agent_data": {"agent_name": "h3"},
        "module_data": [
            {"name": "h3 cpu_percent", "type": "generic_data", "data": 1,
             "extra_data": "nginx:metric:memory"},
        ],
    }
]
count3 = ppt.apply_post_transforms(items3, and_rules)
assert count3 == 0, "AND semantics failed"
assert "min_warning" not in items3[0]["module_data"][0]

# --- Apply over a plain module list (XML/tentacle path) ---------------------

modules = [
    ppt.init_module(
        {
            "name": "x cpu_percent",
            "type": "generic_data",
            "value": "12",
            "extra_data": "nginx:metric:cpu",
        }
    ),
]
countx = ppt.apply_post_transforms(modules, VALID_RULES)
assert countx == 1
xml = ppt.print_module(modules[0])
assert "<min_warning><![CDATA[80]]></min_warning>" in xml, xml
assert "<max_critical><![CDATA[0]]></max_critical>" in xml
assert "<module_group>Rendimiento</module_group>" in xml
assert "<tags>infra:cpu</tags>" in xml

# Multiple tags: comma-separated list passes through verbatim, matching the
# agent's module_tags convention (one <tags> element, server splits it).
multi_tags = """
transform_begin
match_module .*cpu_percent
set_tags infra:cpu,team:ops
transform_end
"""
modules_multi = [
    ppt.init_module(
        {
            "name": "x cpu_percent",
            "type": "generic_data",
            "value": "12",
            "extra_data": "nginx:metric:cpu",
        }
    ),
]
ppt.apply_post_transforms(modules_multi, multi_tags)
assert modules_multi[0]["tags"] == "infra:cpu,team:ops"
xml_multi = ppt.print_module(modules_multi[0])
assert "<tags>infra:cpu,team:ops</tags>" in xml_multi, xml_multi

# set_alert_template appends to the alert list and reaches <alert_template>.
alert_rules = """
transform_begin
match_module .*cpu_percent
set_alert_template Critical mail
transform_end
"""
modules2 = [ppt.init_module({"name": "x cpu_percent", "type": "generic_data", "value": "12"})]
ppt.apply_post_transforms(modules2, alert_rules)
assert modules2[0]["alert"] == ["Critical mail"]
xml2 = ppt.print_module(modules2[0])
assert "<alert_template><![CDATA[Critical mail]]></alert_template>" in xml2, xml2

# --- Tolerant parsing: one bad rule never kills the whole run ---------------

# A typo in one rule skips that rule; the valid rules still apply.
mixed_rules = """
transform_begin
match_module .*good_one.*
set_min_warning 42
transform_end

transform_begin
match_module .*bad.*
set_min_warnig 99
transform_end

transform_begin
match_module .*good_two.*
set_max_critical 7
transform_end
"""
rules_t, errors_t = ppt.parse_transform_blocks_tolerant(mixed_rules)
assert len(rules_t) == 2, "expected the two good rules, got %d" % len(rules_t)
assert rules_t[0]["set"]["min_warning"] == 42
assert rules_t[1]["set"]["max_critical"] == 7
assert len(errors_t) == 1, errors_t
assert "block 2" in errors_t[0] and "min_warnig" in errors_t[0], errors_t[0]

# A bad regex only kills its own rule.
bad_regex_rules = """
transform_begin
match_module .*good.*
set_min_warning 42
transform_end

transform_begin
match_module ([unclosed
set_min_warning 1
transform_end
"""
rules_r, errors_r = ppt.parse_transform_blocks_tolerant(bad_regex_rules)
assert len(rules_r) == 1
assert len(errors_r) == 1 and "invalid regex" in errors_r[0], errors_r

# Tolerant API on empty text: no rules, no errors.
rules_empty, errors_empty = ppt.parse_transform_blocks_tolerant("")
assert rules_empty == [] and errors_empty == []

print("ok")
