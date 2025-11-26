import csv
import logging
import os
from pathlib import Path

import pytest

from pipelines import area_symbols_to_urls


def _read_tsv(path: Path) -> list[tuple[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.reader(fh, delimiter="\t")
        next(reader)  # skip header
        return [tuple(row) for row in reader]


def test_build_urls_respects_missing_dates(monkeypatch, caplog, tmp_path):
    caplog.set_level(logging.WARNING)

    symbols = ["CA803", "CA805", "CA999"]
    monkeypatch.setattr(area_symbols_to_urls, "get_area_symbols", lambda: symbols)

    def fake_fetch(symbols_to_fetch):
        assert symbols_to_fetch == symbols
        return [
            {"area-symbol": "CA803", "date": "9/9/2025"},
            {"area-symbol": "CA805", "date": "2025-09-08"},
        ]

    monkeypatch.setattr(area_symbols_to_urls.nrcs_to_google_cloud_storage, "fetch_sacatalog_records", fake_fetch)

    output = tmp_path / "urls.tsv"
    area_symbols_to_urls.main(output=output)
    rows = _read_tsv(output)
    assert rows == [
        (
            "CA803",
            "https://websoilsurvey.sc.egov.usda.gov/DSD/Download/Cache/SSA/wss_SSA_CA803_soildb_US_2003_[2025-09-09].zip",
        ),
        (
            "CA805",
            "https://websoilsurvey.sc.egov.usda.gov/DSD/Download/Cache/SSA/wss_SSA_CA805_soildb_US_2003_[2025-09-08].zip",
        ),
    ]
    assert "No saverest date for CA999" in caplog.text


def test_main_respects_limit(monkeypatch, tmp_path):
    symbols = ["CA803", "CA805", "CA999"]
    monkeypatch.setattr(area_symbols_to_urls, "get_area_symbols", lambda: symbols)
    outputs = []

    def fake_fetch(symbols_to_fetch):
        outputs.append(list(symbols_to_fetch))
        return [{"area-symbol": sym, "date": "9/9/2025"} for sym in symbols_to_fetch]

    monkeypatch.setattr(area_symbols_to_urls.nrcs_to_google_cloud_storage, "fetch_sacatalog_records", fake_fetch)

    dest = tmp_path / "limited.tsv"
    area_symbols_to_urls.main(output=dest, limit=2)

    rows = _read_tsv(dest)
    assert len(rows) == 2
    assert outputs == [["CA803", "CA805"]]
