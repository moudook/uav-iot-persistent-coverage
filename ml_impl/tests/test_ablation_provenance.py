from __future__ import annotations

import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "analysis"))

from make_tables import _validated_ablation_rows  # noqa: E402
from merge_ablation import _merge_part_rows  # noqa: E402
from uav_wireless.env import SimConfig  # noqa: E402
from uav_wireless.experiments import _ablation_config_hash  # noqa: E402


class TestAblationProvenance(unittest.TestCase):
    @staticmethod
    def row(model, config_hash="generation-a", episodes=25):
        return {
            "model": model,
            "config_hash": config_hash,
            "episodes": str(episodes),
            "train_seeds": "8",
            "device": "cpu",
        }

    def test_merge_rejects_duplicate_model_rows(self):
        with self.assertRaisesRegex(ValueError, "duplicate model row: Full"):
            _merge_part_rows([[self.row("Full")], [self.row("Full")]])

    def test_merge_accepts_unique_rows_from_one_generation(self):
        rows, protocol = _merge_part_rows([
            [self.row("Full")],
            [self.row("no-map")],
        ])
        self.assertEqual(set(rows), {"Full", "no-map"})
        self.assertEqual(protocol, ("25", "8", "cpu"))

    def test_merge_rejects_missing_config_hash(self):
        row = self.row("Full")
        row.pop("config_hash")
        with self.assertRaisesRegex(ValueError, "missing config_hash"):
            _merge_part_rows([[row]])

    def test_merge_rejects_mixed_config_hashes(self):
        with self.assertRaisesRegex(ValueError, "one config_hash"):
            _merge_part_rows([[
                self.row("Full", "generation-a"),
                self.row("no-map", "generation-b"),
            ]])

    def test_merge_rejects_mixed_protocols(self):
        with self.assertRaisesRegex(ValueError, "one protocol"):
            _merge_part_rows([[
                self.row("Full", episodes=25),
                self.row("no-map", episodes=20),
            ]])

    def test_table_rejects_duplicate_model_rows(self):
        with self.assertRaisesRegex(ValueError, "duplicate ablation model row"):
            _validated_ablation_rows([
                self.row("Full"),
                self.row("Full"),
            ])

    def test_table_rejects_mixed_config_hashes(self):
        with self.assertRaisesRegex(ValueError, "one config_hash"):
            _validated_ablation_rows([
                self.row("Full", "generation-a"),
                self.row("no-map", "generation-b"),
            ])

    def test_table_accepts_legacy_rows_without_hashes(self):
        rows = _validated_ablation_rows([
            {"model": "Full"},
            {"model": "no-map"},
        ])
        self.assertEqual(set(rows), {"Full", "no-map"})

    def test_config_hash_tracks_protocol_but_not_training_seed(self):
        variants = {"Full": {}, "no-map": {"map_grid": 0}}
        first = _ablation_config_hash(
            SimConfig(seed=1), False, 25, 5, 8, "cpu", variants)
        same = _ablation_config_hash(
            SimConfig(seed=7), False, 25, 5, 8, "cpu", variants)
        changed = _ablation_config_hash(
            SimConfig(R_cov=30.0), False, 25, 5, 8, "cpu", variants)
        assert first == same
        assert first != changed
