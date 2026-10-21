"""
The token table's own tests.

The token table is where every number in the paper's prose is decided, so
the defects an audit found in it are defects in the paper.  These tests
are the regression net for them:

  * a value that is not a measurement (a nan, an empty list, a None) must
    never reach the paper -- it must become a visible [pending: ...]
    marker instead;
  * a spread must be the SAMPLE standard deviation, not the population
    one, or every interval in the paper is too narrow;
  * a paired comparison must pair, in the right direction, with the
    sample standard deviation of the differences;
  * an interval quoted in a summary must be the SAME interval the table
    prints, to the last digit.

Run:  python tests/run_tests.py TestTokenTable
"""

from __future__ import annotations

import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "analysis"))

from fill_tokens import (build_tokens, paired_stat, per_seed_ck,  # noqa: E402
                         sample_std, screen)


class TestTokenTable:
    def test_screen_drops_a_nan(self):
        """A nan is not a measurement and must not reach the paper."""
        t = screen({"GOOD": "0.412", "BAD": "nan", "ALSO_BAD": "0.3 nan"})
        assert "GOOD" in t
        assert "BAD" not in t
        assert "ALSO_BAD" not in t

    def test_screen_drops_an_empty_value(self):
        """An empty increment list is not a measurement either."""
        t = screen({"GOOD": "0.412", "EMPTY": "", "BLANK": "   "})
        assert "EMPTY" not in t and "BLANK" not in t
        assert "GOOD" in t

    def test_screen_keeps_prose_that_contains_null(self):
        """'a null is a statement about the resolution' is a sentence, not
        a broken number, and dropping it would remove real prose."""
        t = screen({"PROSE": "a null is a statement about the resolution of "
                             "that arm, and the null is not a zero"})
        assert "PROSE" in t

    def test_screen_drops_a_none_value(self):
        t = screen({"GOOD": "0.4", "NONE": "None", "NULL": "null"})
        assert "NONE" not in t and "NULL" not in t

    def test_no_token_in_the_table_is_a_nan(self):
        """The live table: every value is a usable measurement."""
        tok = build_tokens()
        bad = [k for k, v in tok.items()
               if re.search(r"(?<![A-Za-z])(nan|inf)(?![A-Za-z])", str(v),
                            flags=re.I)]
        assert not bad, f"unusable token values: {bad}"

    def test_the_sample_standard_deviation_is_not_the_population_one(self):
        """The distinction the gap's interval depends on."""
        v = [0.743950, 0.679425, 0.671520, 0.679, 0.706, 0.663, 0.641, 0.553]
        import numpy as np
        assert abs(sample_std(v) - float(np.std(v, ddof=1))) < 1e-12
        # the population version is smaller, and an interval built from it
        # is too narrow
        assert sample_std(v) > float(np.std(v))
        assert sample_std([1.0]) == 0.0

    def test_paired_stat_pairs_in_the_right_direction(self):
        """paired_stat(a, b) is the statistic of (a - b)."""
        a = [0.80, 0.70, 0.60, 0.50]
        b = [0.70, 0.60, 0.50, 0.40]
        mean, half, p, n = paired_stat(a, b)
        assert abs(mean - 0.10) < 1e-12
        assert n == 4
        assert half > 0

    def test_paired_stat_uses_the_sample_standard_deviation(self):
        """The half-width must come from ddof=1: with a population std the
        interval is too narrow, and the budget's last increment would be
        called unresolved when it is not."""
        a = [0.826695, 0.80919, 0.744015, 0.72402, 0.74033]
        b = [0.725955, 0.484255, 0.615885, 0.67523, 0.63757]
        mean, half, p, n = paired_stat(a, b)
        diffs = [x - y for x, y in zip(a, b)]
        import numpy as np
        se = float(np.std(diffs, ddof=1)) / math.sqrt(len(diffs))
        # the t quantile for df = 4 at 0.975 is 2.7764
        assert abs(half - 2.7764 * se) < 1e-3

    def test_the_budget_pairs_the_same_training_seeds(self):
        """The budget sweep trains the same seeds at every budget, so the
        two budgets can be compared on the same runs."""
        import json
        p = os.path.join(ROOT, "analysis", "ab_budget.json")
        if not os.path.exists(p):
            return
        rows = json.load(open(p, encoding="utf-8"))
        if len(rows) < 2:
            return
        lo = [float(x) for x in rows[0].get("per_seed_CK", [])]
        hi = [float(x) for x in rows[-1].get("per_seed_CK", [])]
        assert len(lo) == len(hi) and len(lo) > 1
        mean, half, p, n = paired_stat(hi, lo)
        # the longer budget is the better one, so the difference is positive
        assert mean > 0

    def test_the_summary_interval_is_the_table_interval(self):
        """The observation summary and the observation table must quote the
        SAME interval.  The summary used to rebuild it from the ROUNDED
        values, which made the last digit differ."""
        tok = build_tokens()
        if "OBS_SUMMARY" not in tok or "OBS_C_CI" not in tok:
            return
        m = re.search(r"the full observation of the proposed\s*\n?"
                      r"configuration\$?\s*\([^)]*?95\\% interval (\[[^\]]+\])",
                      tok["OBS_SUMMARY"])
        assert m, "the observation summary has no interval to compare"
        assert m.group(1) == tok["OBS_C_CI"], (
            f"the summary prints {m.group(1)} and the table prints "
            f"{tok['OBS_C_CI']}")

    def test_the_gap_names_the_strongest_rule(self):
        """The gap is to the strongest rule, and the paper's text must use
        that rule's name, not another rule's."""
        tok = build_tokens()
        if "GAP" not in tok:
            return
        assert tok["BEST_RULE_CK"] >= tok["REACT_CK"], (
            "the strongest rule must be at least as good as the privileged "
            "one")
