#!/usr/bin/env bash
set -euo pipefail

# -------------------------------
# User placeholders (edit these)
# -------------------------------
DB_PATH="/home/gusmmm/Desktop/burn_unit_db_sqlite/private/database.db"
BACKUP_DIR="/home/gusmmm/gustavo_sync/UQ/database"
# Example:
# DB_PATH="/home/gusmmm/Desktop/burn_unit_db_sqlite/private/database.db"
# BACKUP_DIR="/home/gusmmm/Desktop/burn_unit_db_sqlite/tests/backups"

# Optional prefix for backup filename
BACKUP_PREFIX="sqlite_backup"

if [[ "$DB_PATH" == "__SQLITE_DB_PATH__" ]] || [[ -z "$DB_PATH" ]]; then
  echo "Error: set DB_PATH in this script."
  exit 1
fi

if [[ "$BACKUP_DIR" == "__BACKUP_OUTPUT_DIR__" ]] || [[ -z "$BACKUP_DIR" ]]; then
  echo "Error: set BACKUP_DIR in this script."
  exit 1
fi

if [[ ! -f "$DB_PATH" ]]; then
  echo "Error: database file not found: $DB_PATH"
  exit 1
fi

mkdir -p "$BACKUP_DIR"

timestamp="$(date +%F_%H%M%S)"
backup_path="${BACKUP_DIR}/${BACKUP_PREFIX}_${timestamp}.db"

# SQLite online backup API via CLI: safe while DB is in use.
sqlite3 "$DB_PATH" ".backup '$backup_path'"

check_result="$(sqlite3 "$backup_path" "PRAGMA integrity_check;")"
if [[ "$check_result" != "ok" ]]; then
  echo "Backup created but integrity_check failed: $check_result"
  exit 2
fi

echo "Backup created successfully: $backup_path"
