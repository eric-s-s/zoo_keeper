#!/usr/bin/env bash


data_dir="../data"

zoo_keeper_path="$data_dir/test_zoo_keeper_data.txt"

if [ ! -e $zoo_keeper_path ]; then
    echo "did not provide a correct argument for path to data";
    exit;
fi


eval "$(./export_db_values.sh)"

./drop_all.sh


mysql -h${host} -u${user} ${db} < create_tables.sql

function prepare_values {
    out=${1//,/\",\"}
    out="(\"${out}\")"
    out=${out//\"\"/NULL}
    echo ${out}
    
}

readarray -t zoo_keeper_lines < $zoo_keeper_path
for el in "${zoo_keeper_lines[@]}"; do
    if [[ $el != \#* ]]; then
        values="$(prepare_values "$el")"
        mysql -h${host} -u${user} ${db} -e "
        INSERT INTO zoo_keeper (name, age, zoo_id, favorite_monkey_id, dream_monkey_id) 
        VALUES $values;
        "
    fi
done
