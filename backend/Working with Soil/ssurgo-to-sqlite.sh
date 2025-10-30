#!/usr/bin/env bash
# Converts NRCS SSURGO .mdb file (like AZ649.mdb) into an SQLite database
# Requires: mdbtools, sqlite3
# Usage: ./convert_ssurgo_to_sqlite.sh AZ649.mdb

set -euo pipefail

# --- Config ---
MDB_FILE="${1:-}"
DB_NAME="ssurgo_az649.db"
TMP_DIR="ssurgo_tmp"

if [[ -z "$MDB_FILE" ]]; then
  echo "Usage: $0 <path_to_mdb_file>"
  exit 1
fi

if [[ ! -f "$MDB_FILE" ]]; then
  echo "Error: File not found: $MDB_FILE"
  exit 1
fi

# --- Check dependencies ---
if ! command -v mdb-tables &>/dev/null; then
  echo "mdbtools not found. Installing..."
  brew install mdbtools || sudo apt-get install -y mdbtools
fi

if ! command -v sqlite3 &>/dev/null; then
  echo "sqlite3 not found. Installing..."
  brew install sqlite || sudo apt-get install -y sqlite3
fi

# --- Setup workspace ---
mkdir -p "$TMP_DIR"
rm -f "$DB_NAME"

echo "Converting $MDB_FILE -> $DB_NAME"
echo "Intermediate files in: $TMP_DIR"

# --- Export tables from MDB ---
tables=$(mdb-tables -1 "$MDB_FILE" | grep -v '^\s*$' || true)
echo "Found $(echo "$tables" | wc -l) tables."

for t in $tables; do
  echo "Exporting table: $t"
  safe_name=$(echo "$t" | tr -d '[:space:]' | tr '[:upper:]' '[:lower:]')
  csv_file="$TMP_DIR/${safe_name}.csv"

  # Export to CSV
  mdb-export -D "%Y-%m-%dT%H:%M:%S" "$MDB_FILE" "$t" > "$csv_file" || {
    echo "Warning: failed to export $t"
    continue
  }

  # Import into SQLite
  echo "Importing into SQLite: $safe_name"
  sqlite3 "$DB_NAME" <<SQL
.mode csv
.import '$csv_file' '$safe_name'
SQL

done

# --- Verify ---
echo "SQLite conversion complete!"
echo "Tables in $DB_NAME:"
sqlite3 "$DB_NAME" ".tables"

# --- Cleanup ---
echo "Cleaning up temporary files..."
rm -rf "$TMP_DIR"

echo "Done. SQLite DB ready: $DB_NAME"
