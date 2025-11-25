import asyncio
import sys
from pathlib import Path

SCRIPT_ROOT = Path(__file__).resolve().parent
BACKEND_ROOT = SCRIPT_ROOT.parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from pipelines import nrcs_to_google_cloud_storage


def _validate_args(args: list[str]) -> str:
    if len(args) != 2:
        raise SystemExit(f"Usage: {args[0]} <manifest-path>")
    return args[1]


if __name__ == "__main__":
    manifest_path = _validate_args(sys.argv)
    asyncio.run(nrcs_to_google_cloud_storage.main(manifest_path))
