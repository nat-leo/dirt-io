import asyncio
import io
import zipfile
from typing import List
import httpx
from google.cloud import storage

CONCURRENCY = 50
GCS_BUCKET = "soil-raw"

storage_client = storage.Client()
bucket = storage_client.bucket(GCS_BUCKET)

async def fetch_zip(client: httpx.AsyncClient, url: str) -> bytes:
    resp = await client.get(url, timeout=60)
    resp.raise_for_status()
    return resp.content

def upload_to_gcs(path: str, data: bytes) -> None:
    blob = bucket.blob(path)
    blob.upload_from_string(data)

async def process_url(semaphore: asyncio.Semaphore, client: httpx.AsyncClient, url: str):
    async with semaphore:
        zip_bytes = await fetch_zip(client, url)

    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as z:
        for name in z.namelist():
            # TODO: derive state/county from URL or filename
            gcs_path = f"ingest_date=2025-11-21/raw/{name}"
            with z.open(name) as f:
                data = f.read()
            upload_to_gcs(gcs_path, data)

async def main(manifest_path: str):
    # Read manifest (either from local or GCS; if GCS, use google-cloud-storage to download first)
    with open(manifest_path) as f:
        urls = [line.strip() for line in f if line.strip()]

    sem = asyncio.Semaphore(CONCURRENCY)
    async with httpx.AsyncClient() as client:
        tasks = [
            asyncio.create_task(process_url(sem, client, url))
            for url in urls
        ]
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    import sys
    asyncio.run(main(sys.argv[1]))
