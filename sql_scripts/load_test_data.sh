#!/usr/bin/env bash

#if [ ! -d "$(pwd)/sql_scripts" ]; then 
#    echo "must be called from project top directory";
#    exit;
#fi


#data_dir=$( test $1 && echo $1 || echo . )

data_dir="../zoo_keeper_server/data"

zoo_keeper_path="$data_dir/zoo_keeper_data.txt"

if [ ! -e $zoo_keeper_path ]; then
    echo "did not provide a correct argument for path to data";
    exit;
fi


eval "$(./export_db_values.sh)"

./drop_all.sh


mysql $db -u $user < create_tables.sql

function prepare_values {
    out=${1//,/\",\"}
    echo "(\"${out}\")"
}

readarray -t zoo_keeper_lines < $zoo_keeper_path
for el in "${zoo_keeper_lines[@]}"; do
    if [[ $el != \#* ]]; then
        values="$(prepare_values "$el")"
        mysql -u $user $db -e "INSERT INTO zoo (name, age, zoo_id, favorite_monkey_id, dream_monkey_id) VALUES $values;"
    fi

