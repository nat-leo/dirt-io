# NRCS to GCS Pipeline

`backend/pipelines/nrcs-to-google-cloud-storage.py` is a thin CLI wrapper around the reusable logic in `pipelines/nrcs_to_google_cloud_storage.py`.

The wrapper ensures the project root is on `sys.path`, so you can keep running `python backend/pipelines/nrcs-to-google-cloud-storage.py --manifest path/to/manifest.txt` without changing your invocation. The underlying module can also be used directly via `pipelines.nrcs_to_google_cloud_storage`.

### CLI options

| Option | Description |
| --- | --- |
| `-m`/`--manifest <path>` | Download every URL listed in the file, uncompress each archive, and upload to GCS. |
| `-a`/`--area-symbol <symbol>` | Fetch the `saverest` date from NRCS (`sacatalog`), build the Web Soil Survey ZIP URL (logs it), download that single package, and upload it. Ideal for quick smoke tests. |
| `-b`/`--bucket <name>` | Override the target bucket (defaults to `GCS_BUCKET` env var or `soil-raw`). |
| `-c`/`--concurrency <n>` | Number of concurrent downloads when you use `--manifest` (default: `50`). |

When you need to test just one area symbol before a mass ingest (e.g., `--area-symbol CA805`), the utility queries `sacatalog` with `SELECT areasymbol, saverest FROM sacatalog WHERE areasymbol IN (...)`, converts the returned date to `YYYY-MM-DD`, constructs a URL such as `https://websoilsurvey.sc.egov.usda.gov/DSD/Download/Cache/SSA/wss_SSA_CA805_soildb_US_2003_[2025-09-09].zip`, logs it, and uploads the unzipped contents.

Set `GCS_BUCKET=soil-parcels-of` (or pass `--bucket soil-parcels-of`) to stage those smoke-test downloads alongside your production data.

## Skippable integration check

Before committing to a massive download, run the optional `pytest` integration test that hits a small manifest:

```bash
export RUN_NRCSDOWNLOAD_TEST=1
export NRCSDOWNLOAD_TEST_MANIFEST=/path/to/a/manually-curated-test-manifest.txt
python -m pytest backend/tests/test_nrcs_pipeline_download.py -q
```

The manifest should list a few URLs, one per line, pointing to the NRCS artifacts you care about. The test patches `upload_to_gcs` so you only verify downloads and unpacking, not a real GCS upload. If you leave `RUN_NRCSDOWNLOAD_TEST` unset, the test is skipped so it does not run on every CI invocation.
