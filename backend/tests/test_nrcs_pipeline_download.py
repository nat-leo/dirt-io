import asyncio
import io
import logging
import os
import sys
import zipfile
from pathlib import Path

import pytest

# ensure the pipelines directory is importable the same way other backend tests work
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pipelines import nrcs_to_google_cloud_storage

SKIP_REASON = (
    "NRCS download test is not enabled by default because it requires live GCS "
    "credentials, network access, and a curated manifest. Set RUN_NRCSDOWNLOAD_TEST=1 "
    "and point NRCSDOWNLOAD_TEST_MANIFEST at a small manifest to execute."
)


@pytest.mark.skipif(os.getenv("RUN_NRCSDOWNLOAD_TEST") != "1", reason=SKIP_REASON)
def test_nrcs_pipeline_manifest_download(monkeypatch):
    manifest_path = os.getenv("NRCSDOWNLOAD_TEST_MANIFEST")
    if not manifest_path:
        pytest.skip("NRCSDOWNLOAD_TEST_MANIFEST is not set")

    manifest = Path(manifest_path)
    assert manifest.exists(), f"{manifest} must exist to run this integration test"

    uploaded_paths: list[str] = []

    def fake_upload(path: str, data: bytes, *, bucket_name: str | None = None) -> None:
        uploaded_paths.append(path)

    monkeypatch.setattr(nrcs_to_google_cloud_storage, "upload_to_gcs", fake_upload)

    asyncio.run(nrcs_to_google_cloud_storage.main(manifest_path, concurrency=2))

    assert uploaded_paths, "The manifest should have resulted in at least one upload call"


def _make_dummy_zip() -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as archive:
        archive.writestr("test.txt", "dummy")
    return buf.getvalue()


def test_upload_archive_with_custom_prefix(monkeypatch):
    zip_bytes = _make_dummy_zip()
    captured: list[str] = []

    def fake_upload(path: str, data: bytes, *, bucket_name: str | None = None, **kwargs):
        captured.append(path)

    monkeypatch.setattr(nrcs_to_google_cloud_storage, "upload_to_gcs", fake_upload)

    nrcs_to_google_cloud_storage.upload_archive(
        zip_bytes,
        bucket_name="soil-parcels-of",
        path_prefix="custom-prefix",
        show_progress=False,
    )

    assert captured == ["custom-prefix/test.txt"]


def test_upload_archive_without_prefix(monkeypatch):
    zip_bytes = _make_dummy_zip()
    captured: list[str] = []

    def fake_upload(path: str, data: bytes, *, bucket_name: str | None = None, **kwargs):
        captured.append(path)

    monkeypatch.setattr(nrcs_to_google_cloud_storage, "upload_to_gcs", fake_upload)

    nrcs_to_google_cloud_storage.upload_archive(
        zip_bytes,
        bucket_name="soil-parcels-of",
        show_progress=False,
    )

    assert captured == ["test.txt"]


def test_download_area_symbol_package(monkeypatch, caplog):
    zip_bytes = _make_dummy_zip()
    urls: list[str] = []
    recorded_paths: list[str] = []

    def fake_records(symbols):
        assert list(symbols) == ["CA805"]
        return [{"area-symbol": "CA805", "date": "9/9/2025"}]

    async def fake_fetch_zip(client, url, *, desc: str = ""):
        urls.append(url)
        return zip_bytes

    def fake_upload_to_gcs(
        path: str,
        data: bytes,
        *,
        bucket_name: str | None = None,
        **kwargs,
    ) -> None:
        recorded_paths.append(path)

    monkeypatch.setattr(nrcs_to_google_cloud_storage, "fetch_sacatalog_records", fake_records)
    monkeypatch.setattr(
        nrcs_to_google_cloud_storage,
        "fetch_zip_with_progress",
        fake_fetch_zip,
    )
    monkeypatch.setattr(nrcs_to_google_cloud_storage, "upload_to_gcs", fake_upload_to_gcs)

    caplog.set_level(logging.INFO)
    asyncio.run(
        nrcs_to_google_cloud_storage.download_area_symbol_package(
            "CA805",
            bucket_name="soil-parcels-of",
        ),
    )

    assert recorded_paths == ["test.txt"]
    assert urls and "2025-09-09" in urls[0]
    assert "2025-09-09" in caplog.text
