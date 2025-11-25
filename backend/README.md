# Backend services

The backend provides:

- `soil.py`: a FastAPI app that proxies USDA Soil Data Access most-used endpoints (coordinate lookup + SQL POST) while handling CORS and error handling.
- `area_symbol_utils.py`: helpers for reading `area-symbols.json`, flattening the mapping, and exposing a single list of every `areasymbol` stored under `backend/area-symbols.json`.
- `pipelines/`: importable download helpers for pulling NRCS ZIP bundles and streaming them into Google Cloud Storage, plus a CLI shim (`pipelines/nrcs-to-google-cloud-storage.py`) for backward compatibility.

## Setup

1. Activate the backend virtualenv from `backend/venv`:

```bash
cd backend
source ./venv/bin/activate
```

2. Install any missing dependencies using `pip install -r requirements.txt`.

3. Set environment variables as needed:
   - `AREA_SYMBOLS_PATH` if you want to override `backend/area-symbols.json`.
   - `FRONTEND_ORIGIN` to allow a custom frontend during local dev.

## Running

- **FastAPI**: `uvicorn soil:app --reload` from the `backend/` directory when the virtualenv is active.
- **Area symbols helper**: import `area_symbol_utils.read_area_symbol_values()` from other modules to consistently use the canonical list.
- **NRCS pipeline**: run `python pipelines/nrcs-to-google-cloud-storage.py <manifest>` from the `backend/` directory. The CLI ensures the module path resolves before invoking the shared async logic that downloads manifests, unzips, and uploads to GCS.

## Tests

1. Activate the backend virtualenv.
2. Run unit tests with `python -m pytest backend/tests`.
3. There is an optional integration/smoke test for the NRCS download pipeline:

```bash
export RUN_NRCSDOWNLOAD_TEST=1
export NRCSDOWNLOAD_TEST_MANIFEST=/path/to/a/short-manifest.txt
python -m pytest backend/tests/test_nrcs_pipeline_download.py -q
```

The test patches `upload_to_gcs` so it only verifies downloading and unpacking. Leave `RUN_NRCSDOWNLOAD_TEST` unset to skip this slower test in CI/typical workflows.
