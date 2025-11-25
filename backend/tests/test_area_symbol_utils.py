import json
import os
import sys
from pathlib import Path

import pytest

# Make backend modules importable alongside soil tests.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from area_symbol_utils import (
    build_sacatalog_date_query,
    flatten_area_symbols,
    load_area_symbols,
    parse_sacatalog_dates,
    read_area_symbol_values,
)


def test_flatten_area_symbols_returns_ordered_flat_list():
    mock_data = {
        "CA": ["CA001", "CA002"],
        "KS": ["KS010"],
    }
    assert flatten_area_symbols(mock_data) == ["CA001", "CA002", "KS010"]


def test_load_area_symbols_rejects_non_object(tmp_path):
    bad_file = tmp_path / "area-symbols.json"
    bad_file.write_text(json.dumps(["not", "an", "object"]))

    with pytest.raises(ValueError):
        load_area_symbols(bad_file)


def test_read_area_symbol_values_from_file(tmp_path):
    sample_file = tmp_path / "area-symbols.json"
    payload = {
        "WA": ["WA001"],
        "OR": ["OR014", "OR015"],
    }
    sample_file.write_text(json.dumps(payload))

    values = read_area_symbol_values(sample_file)

    assert values == ["WA001", "OR014", "OR015"]


def test_flatten_area_symbols_rejects_invalid_entry():
    with pytest.raises(ValueError):
        flatten_area_symbols({"CA": "CA001"})


def test_build_sacatalog_date_query_handles_duplicates_and_trims():
    query = build_sacatalog_date_query(["CA803", " CA805 ", "CA803"])
    assert "CA803" in query
    assert "CA805" in query
    assert query.count("CA803") == 1


def test_build_sacatalog_date_query_rejects_empty_input():
    with pytest.raises(ValueError):
        build_sacatalog_date_query([])


def test_parse_sacatalog_dates_filters_invalid_rows():
    resp = {
        "Table": [
            ["CA803", "9/9/2025 5:37:47 PM"],
            ["CA805", "9/8/2025 9:48:46 PM"],
            ["CA810"],
            [123, "9/7/2025 3:00:00 PM"],
            ["CA811", None],
        ]
    }

    parsed = parse_sacatalog_dates(resp)

    assert parsed == [
        {"area-symbol": "CA803", "date": "9/9/2025"},
        {"area-symbol": "CA805", "date": "9/8/2025"},
        {"area-symbol": "CA811", "date": ""},
    ]


def test_parse_sacatalog_dates_returns_empty_for_missing_table():
    assert parse_sacatalog_dates({}) == []
