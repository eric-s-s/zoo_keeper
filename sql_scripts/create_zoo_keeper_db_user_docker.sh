#!/usr/bin/env bash
eval "$(./export_db_values.sh)"



sudo mysql -h${host} -uroot -p -e  "
    CREATE DATABASE IF NOT EXISTS ${db};
    CREATE DATABASE IF NOT EXISTS test;
    DROP USER IF EXISTS '${user}'@'%';
    CREATE USER '${user}'@'%';
    GRANT ALL ON ${db}.* TO '${user}'@'%';
    GRANT ALL ON test.* TO '${user}'@'%';
    "
