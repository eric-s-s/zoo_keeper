#!/usr/bin/env bash

usr="keeper_guest"
db="keeper"

tables=$(mysql -u ${usr} ${db} -e 'show tables;' | sed -e '/^Tables_in/d')

printf "removing these tables:\n$tables\n\n"


safety_off="set foreign_key_checks = 0;"
safety_on="set foreign_key_checks = 1;"


for t in ${tables[@]}
do
    echo "bye $t"
    mysql -u $usr $db -e "$safety_off drop table if exists $t; $safety_on"
done

