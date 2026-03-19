# import municipios into the addresses table
sqlite3 database/database.db <<'SQL'
.mode csv
.import --skip 1 tests/addresses_municipios.csv addresses
SQL

