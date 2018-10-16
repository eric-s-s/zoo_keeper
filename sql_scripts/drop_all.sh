#!/usr/bin/env bash

eval "$(./export_db_values.sh)"

tables=$(mysql -h${host} -u${user} ${db} -e 'show tables;' | sed -e '/^Tables_in/d')

printf "removing these tables:\n$tables\n\n"


safety_off="set foreign_key_checks = 0;"
safety_on="set foreign_key_checks = 1;"


for t in ${tables[@]}
do
    echo "bye $t"
    mysql -h${host} -u${user} ${db} -e "${safety_off} drop table if exists ${t}; ${safety_on}"
done

