# open the local database 
sqlite3 -readonly -init database/local_config.sql database/database.db 
# import municipios into the addresses table
sqlite3 database/database.db <<'SQL'
.mode csv
.import --skip 1 tests/addresses_municipios.csv addresses
SQL

