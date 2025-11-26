from __future__ import annotations

import argparse
import csv
import logging
from pathlib import Path
from typing import Iterable, Iterator, Sequence

from pipelines import nrcs_to_google_cloud_storage
from soil import get_area_symbols

logger = logging.getLogger(__name__)


def chunked(sequence: Sequence[str], size: int) -> Iterator[list[str]]:
    for start in range(0, len(sequence), size):
        yield sequence[start : start + size]


def build_urls(symbols: Sequence[str]) -> list[tuple[str, str]]:
    records_by_symbol: dict[str, str] = {}

    for group in chunked(symbols, 50):
        records = nrcs_to_google_cloud_storage.fetch_sacatalog_records(group)
        for record in records:
            symbol = record.get("area-symbol")
            date = record.get("date", "")
            if symbol and date:
                try:
                    iso = nrcs_to_google_cloud_storage.iso_date(date)
                except ValueError:
                    logger.warning("Skipping %s because date %r was unparseable", symbol, date)
                else:
                    records_by_symbol[symbol] = iso
            else:
                logger.warning("Missing data for %s", symbol)

    results: list[tuple[str, str]] = []
    for symbol in symbols:
        date_iso = records_by_symbol.get(symbol)
        if not date_iso:
            logger.warning("No saverest date for %s", symbol)
            continue
        url = nrcs_to_google_cloud_storage.build_zip_url(symbol, date_iso)
        results.append((symbol, url))

    return results


def write_tsv(rows: Sequence[tuple[str, str]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh, delimiter="\t")
        writer.writerow(["areasymbol", "url"])
        writer.writerows(rows)


def main(
    *,
    output: Path,
    limit: int | None = None,
) -> None:
    symbols = get_area_symbols()
    if limit:
        symbols = symbols[:limit]

    rows = build_urls(symbols)
    write_tsv(rows, output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build Web Soil Survey ZIP URLs for every area symbol")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("area-symbol-urls.tsv"),
        help="Path to the TSV file that receives the generated download URLs",
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Limit the number of area symbols processed (handy for testing)",
    )

    args = parser.parse_args()
    main(output=args.output, limit=args.limit)
