from __future__ import annotations

import json
from pathlib import Path

import pytest

pytest.importorskip("crewai")

from tools.flip_ledger import flip_csv_summary  # noqa: E402


def test_flip_csv_summary_tool(project_root: Path) -> None:
    raw = flip_csv_summary.run("revenue_pulse/sample_flips.csv")
    data = json.loads(raw)
    assert data["sold_count"] == 6
    assert data["pending_count"] == 2
