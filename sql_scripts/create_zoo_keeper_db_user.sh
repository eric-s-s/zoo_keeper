eval "$(./export_db_values.sh)"


sudo mysql -e  "
    CREATE DATABASE IF NOT EXISTS ${db};
    DROP USER IF EXISTS '${user}'@'${host}' ;
    CREATE USER '${user}'@'${host}';
    GRANT ALL PRIVILEGES ON ${db}.* TO '${user}'@'${host}';
    GRANT ALL PRIVILEGES ON test.* TO '${user}'@'${host}';
    "
