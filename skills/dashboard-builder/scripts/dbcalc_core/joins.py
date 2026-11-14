"""`join-audit`: the mechanical half of the Join Safety Gate.

references/data-quality-gate.md §1 "Cross-file grain match" and "Join Safety
Gate". This answers the machine-checkable questions 4 cardinality,
5 coverage (match rate) and 8 fan-out (row count after the join vs. each
input); its key-uniqueness counts per side feed question 1 (grain), which
still needs a statement of what one row represents. Question 2 (the join
key) is the analyst's choice, passed in as --keys. Questions 3 (semantic key
equivalence), 6 (additivity at the target grain), 7 (temporal alignment) and
9 (false alignment) need judgement. The verdict (SAFE /
SAFE_AFTER_AGGREGATION / UNSAFE) is therefore a mechanical upper bound,
never a clearance of the judgement questions, and never CONDITIONAL. Counts
only: key values are never printed (keys are often customer or transaction
IDs).
"""
import os

from . import tabular

MIN_COVERAGE = 0.6  # "a join that drops 40% of one side's rows is not a join, it's a filter"


def _keys(path, keys, sheet, casefold):
    tbl = tabular.load(path, sheet)
    typed = tabular.Typed(tbl)
    cols = [typed.texts(k) for k in keys]
    out = []
    nulls = 0
    for row in zip(*cols):
        if any(v in (None, "") for v in row):
            nulls += 1
            out.append(None)
            continue
        out.append(tuple(v.casefold() if casefold else v for v in row))
    return tbl, out, nulls


def _side(keys):
    counts = {}
    for k in keys:
        if k is not None:
            counts[k] = counts.get(k, 0) + 1
    dup_keys = sum(1 for v in counts.values() if v > 1)
    return counts, {"rows": len(keys), "null_key_rows": sum(1 for k in keys if k is None),
                    "distinct_keys": len(counts), "duplicated_keys": dup_keys,
                    "rows_with_duplicated_keys": sum(v for v in counts.values() if v > 1),
                    "key_unique": dup_keys == 0}


def join_audit(left, right, keys, right_keys=None, left_sheet=None, right_sheet=None,
               casefold=False, min_coverage=MIN_COVERAGE):
    rk = right_keys or keys
    if len(rk) != len(keys):
        raise tabular.InputError("--keys and --right-keys need the same number of columns")
    _, lk_vals, _ = _keys(left, keys, left_sheet, casefold)
    _, rk_vals, _ = _keys(right, rk, right_sheet, casefold)
    lc, ls = _side(lk_vals)
    rc, rs = _side(rk_vals)
    matched = set(lc) & set(rc)
    inner = sum(lc[k] * rc[k] for k in matched)
    left_join = sum(lc[k] * rc[k] if k in rc else lc[k] for k in lc) + ls["null_key_rows"]
    l_matched_rows = sum(lc[k] for k in matched)
    r_matched_rows = sum(rc[k] for k in matched)
    l_cov = l_matched_rows / ls["rows"] if ls["rows"] else None
    r_cov = r_matched_rows / rs["rows"] if rs["rows"] else None
    l_many = any(lc[k] > 1 for k in matched)
    r_many = any(rc[k] > 1 for k in matched)
    card = {(False, False): "one-to-one", (False, True): "one-to-many",
            (True, False): "many-to-one", (True, True): "many-to-many"}[(l_many, r_many)]
    reasons = []
    if card == "many-to-many":
        verdict = "UNSAFE"
        reasons.append("many-to-many on the key: duplicate keys on both sides multiply sums "
                       "(near-cartesian fan-out); aggregate each side to the key first")
    elif card != "one-to-one":
        verdict = "SAFE_AFTER_AGGREGATION"
        finer = "right" if card == "one-to-many" else "left"
        reasons.append("%s: the %s file is finer than the key; aggregate it to the key before joining, "
                       "or every sum from the other side is replicated" % (card, finer))
    else:
        verdict = "SAFE"
    for side, cov in (("left", l_cov), ("right", r_cov)):
        if cov is not None and cov < min_coverage:
            verdict = "UNSAFE"
            reasons.append("coverage: only %.1f%% of %s rows match (minimum %.0f%%) — this is a filter, "
                           "not a join" % (cov * 100, side, min_coverage * 100))
    fan_out = inner / max(ls["rows"], rs["rows"]) if max(ls["rows"], rs["rows"]) else None
    return {
        "command": "join-audit",
        "left": {"file": os.path.basename(left), "sheet": left_sheet, "keys": keys, **ls},
        "right": {"file": os.path.basename(right), "sheet": right_sheet, "keys": rk, **rs},
        "matched_distinct_keys": len(matched),
        "unmatched_distinct_keys": {"left_only": len(set(lc) - set(rc)), "right_only": len(set(rc) - set(lc))},
        "coverage": {"left_rows_matched_share": l_cov, "right_rows_matched_share": r_cov},
        "rows_after": {"inner": inner, "left": left_join},
        "fan_out": {"inner_rows_over_larger_input": fan_out,
                    "left_join_rows_over_left_rows": (left_join / ls["rows"]) if ls["rows"] else None,
                    "exceeds_both_inputs": inner > ls["rows"] and inner > rs["rows"]},
        "cardinality": card,
        "mechanical_verdict": verdict,
        "reasons": reasons,
        "gate_coverage": {"answered": ["4 cardinality", "5 coverage", "8 fan-out risk"],
                          "feeds": ["1 grain (key uniqueness per side; what a row represents is still stated "
                                    "by the analyst)"],
                          "analyst_choice": ["2 join key (--keys)"],
                          "verdict": "mechanical upper bound; never CONDITIONAL; never clears 3, 6, 7, 9"},
        "not_machine_checked": ["3 semantic key equivalence", "6 additivity at the target grain",
                                "7 temporal alignment", "9 false alignment risk"],
        "note": "key values are never printed; counts only",
    }
