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

### Generate area symbol download URLs

Use `pipelines.area_symbols_to_urls` when you need a TSV of every Web Soil Survey ZIP URL corresponding to the current `area-symbols.json`. It queries `sacatalog` in batches, converts each `saverest` date to `YYYY-MM-DD`, builds the `wss_SSA_{area_symbol}...[{date}].zip` URL, and writes the results to a tab-separated file.

```bash
cd backend
python -m pipelines.area_symbols_to_urls --output area-symbol-urls.tsv
```

The script logs warnings for any symbols with missing dates and skips them. Pass `--limit 10` during development to only resolve the first ten area symbols.

When you need to test just one area symbol before a mass ingest (e.g., `--area-symbol CA805`), the utility queries `sacatalog` with `SELECT areasymbol, saverest FROM sacatalog WHERE areasymbol IN (...)`, converts the returned date to `YYYY-MM-DD`, constructs a URL such as `https://websoilsurvey.sc.egov.usda.gov/DSD/Download/Cache/SSA/wss_SSA_CA805_soildb_US_2003_[2025-09-09].zip`, logs it, and uploads the unzipped contents.

Set `GCS_BUCKET=soil-parcels-of` (or pass `--bucket soil-parcels-of`) to stage those smoke-test downloads alongside your production data.

### Example area-symbol run

```bash
cd backend
GCS_BUCKET=soil-parcels-of python -m pipelines.nrcs_to_google_cloud_storage --area-symbol CA805
```

The tool logs the zip URL it downloads (`INFO` level), and you’ll see `tqdm` progress bars for the download and unzipping/upload stages so you can gauge how long the full workflow takes. The files are uploaded under `gs://soil-parcels-of/CA805/` so each symbol lands in its own directory. Before running it, authenticate with Google Cloud (`gcloud auth application-default login` or `gcloud auth login` + `export GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json`) so the bucket accepts your upload.

## Skippable integration check

Before committing to a massive download, run the optional `pytest` integration test that hits a small manifest:

```bash
export RUN_NRCSDOWNLOAD_TEST=1
export NRCSDOWNLOAD_TEST_MANIFEST=/path/to/a/manually-curated-test-manifest.txt
python -m pytest backend/tests/test_nrcs_pipeline_download.py -q
```

The manifest should list a few URLs, one per line, pointing to the NRCS artifacts you care about. The test patches `upload_to_gcs` so you only verify downloads and unpacking, not a real GCS upload. If you leave `RUN_NRCSDOWNLOAD_TEST` unset, the test is skipped so it does not run on every CI invocation.
