from __future__ import annotations

import argparse
import asyncio
import io
import logging
import os
import sys
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, Mapping, Sequence

import httpx
from google.cloud import storage
from tqdm import tqdm

from area_symbol_utils import build_sacatalog_date_query, parse_sacatalog_dates

logger = logging.getLogger(__name__)

SDM_URL = "https://sdmdataaccess.nrcs.usda.gov/Tabular/post.rest"
SDM_HEADERS = {"Content-Type": "application/x-www-form-urlencoded"}
SDM_TIMEOUT = 20.0
ZIP_URL_TEMPLATE = (
    "https://websoilsurvey.sc.egov.usda.gov/DSD/Download/Cache/SSA/"
    "wss_SSA_{area_symbol}_soildb_US_2003_[{date}].zip"
)
CONCURRENCY = 50
DEFAULT_GCS_BUCKET = os.getenv("GCS_BUCKET", "soil-raw")
DEFAULT_GCS_PREFIX = os.getenv("GCS_PREFIX", "ingest_date=2025-11-21/raw")
_storage_buckets: Dict[str, storage.bucket.Bucket] = {}


def _get_storage_bucket(bucket_name: str | None = None) -> storage.bucket.Bucket:
    """
    Lazy-load a storage bucket per bucket name to avoid re-creating clients.
    """
    target = bucket_name or DEFAULT_GCS_BUCKET
    bucket = _storage_buckets.get(target)
    if bucket is None:
        bucket = storage.Client().bucket(target)
        _storage_buckets[target] = bucket
    return bucket


async def fetch_zip(client: httpx.AsyncClient, url: str) -> bytes:
    response = await client.get(url, timeout=60)
    response.raise_for_status()
    return response.content


async def fetch_zip_with_progress(client: httpx.AsyncClient, url: str, *, desc: str = "Downloading") -> bytes:
    async with client.stream("GET", url, timeout=60) as response:
        response.raise_for_status()
        total = int(response.headers.get("content-length") or 0)
        progress = tqdm(
            total=total if total > 0 else None,
            unit="B",
            unit_scale=True,
            desc=desc,
            leave=False,
        )
        buffer = bytearray()
        async for chunk in response.aiter_bytes(64 * 1024):
            buffer.extend(chunk)
            progress.update(len(chunk))
        progress.close()
    return bytes(buffer)


def upload_to_gcs(path: str, data: bytes, *, bucket_name: str | None = None) -> None:
    """
    Push a byte payload into the configured GCS bucket.
    """
    bucket = _get_storage_bucket(bucket_name)
    bucket.blob(path).upload_from_string(data)


def upload_archive(
    zip_bytes: bytes,
    *,
    bucket_name: str | None = None,
    path_prefix: str | None = None,
    show_progress: bool = False,
) -> None:
    """
    Extract each file from an archive and upload it to GCS.
    """
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as archive:
        members = archive.namelist()
        progress = tqdm(total=len(members), desc="Unzipping/Uploading", unit="file", leave=False) if show_progress else None
        for name in members:
            with archive.open(name) as fileobj:
                data = fileobj.read()

            prefix = path_prefix or DEFAULT_GCS_PREFIX
            gcs_path = f"{prefix}/{name}"
            upload_to_gcs(gcs_path, data, bucket_name=bucket_name)
            if progress:
                progress.update(1)

        if progress:
            progress.close()


async def process_url(
    semaphore: asyncio.Semaphore,
    client: httpx.AsyncClient,
    url: str,
    *,
    bucket_name: str | None = None,
) -> None:
    async with semaphore:
        zip_bytes = await fetch_zip(client, url)

    upload_archive(zip_bytes, bucket_name=bucket_name)


async def main(
    manifest_path: str,
    *,
    concurrency: int = CONCURRENCY,
    bucket_name: str | None = None,
) -> None:
    """
    Download all URLs listed in the manifest and stream their contents into GCS.
    """
    manifest = Path(manifest_path)
    if not manifest.exists():
        raise FileNotFoundError(f"Manifest not found: {manifest}")

    with manifest.open() as manifest_file:
        urls = [line.strip() for line in manifest_file if line.strip()]

    if not urls:
        return

    semaphore = asyncio.Semaphore(concurrency)
    async with httpx.AsyncClient() as client:
        tasks = [
            asyncio.create_task(
                process_url(semaphore, client, url, bucket_name=bucket_name),
            )
            for url in urls
        ]
        await asyncio.gather(*tasks)


def fetch_sacatalog_records(symbols: Iterable[str]) -> list[Mapping[str, str]]:
    """
    Query NRCS for the saverest dates for the requested area symbols.
    """
    query = build_sacatalog_date_query(symbols)
    payload = {"query": query, "format": "json"}
    response = httpx.post(SDM_URL, data=payload, headers=SDM_HEADERS, timeout=SDM_TIMEOUT)
    response.raise_for_status()
    return parse_sacatalog_dates(response.json())


def iso_date(date_str: str) -> str:
    """
    Normalize dates such as \"9/9/2025\" into ISO format.
    """
    if not date_str:
        return ""

    for fmt in ("%m/%d/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(date_str, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue

    raise ValueError(f"Unable to parse date value {date_str!r}")


def build_zip_url(area_symbol: str, date_iso: str) -> str:
    return ZIP_URL_TEMPLATE.format(area_symbol=area_symbol, date=date_iso)


async def download_area_symbol_package(
    area_symbol: str,
    *,
    bucket_name: str | None = None,
) -> None:
    """
    Fetch the latest ZIP URL for a specific area symbol and upload it to GCS.
    """
    records = fetch_sacatalog_records([area_symbol])
    record = next(
        (row for row in records if row.get("area-symbol") == area_symbol),
        None,
    )
    if not record:
        raise ValueError(f"No records available for {area_symbol}")

    date_value = record.get("date", "")
    if not date_value:
        raise ValueError(f"No saverest date available for {area_symbol}")

    date_iso = iso_date(date_value)
    zip_url = build_zip_url(area_symbol, date_iso)
    logger.info("Downloading NRCS ZIP for %s: %s", area_symbol, zip_url)

    async with httpx.AsyncClient() as client:
        zip_bytes = await fetch_zip_with_progress(client, zip_url, desc=f"Downloading {area_symbol}")

    upload_archive(zip_bytes, bucket_name=bucket_name, show_progress=True, path_prefix=area_symbol)


def run_from_cli(args: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Download NRCS soil ZIP bundles into GCS.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-m", "--manifest", help="Path to a manifest file listing NRCS URLs.")
    group.add_argument("-a", "--area-symbol", help="Download the ZIP for a single area symbol.")
    parser.add_argument(
        "-b",
        "--bucket",
        help="Override the target GCS bucket (defaults to env `GCS_BUCKET` or soil-raw).",
    )
    parser.add_argument(
        "-c",
        "--concurrency",
        type=int,
        default=CONCURRENCY,
        help="Number of concurrent downloads when using a manifest.",
    )

    parsed = parser.parse_args(list(args or sys.argv[1:]))
    bucket_name = parsed.bucket

    if parsed.manifest:
        asyncio.run(
            main(
                parsed.manifest,
                concurrency=parsed.concurrency,
                bucket_name=bucket_name,
            ),
        )
    else:
        asyncio.run(
            download_area_symbol_package(
                parsed.area_symbol,
                bucket_name=bucket_name,
            ),
        )


if __name__ == "__main__":
    run_from_cli()
