#!/usr/bin/env bash
sql_scripts/drop_all.sh
mysql -u keeper_guest keeper < sql_scripts/create_tables.sql

echo "data dir is $1"
python3 load_test_data.py $1
