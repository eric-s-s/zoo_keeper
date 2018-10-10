#!/usr/bin/env bash

./create_test_data.sh data

mysql zoo -u zoo_guest  -e 'select * from zoo;'

mysql zoo -u zoo_guest  -e 'select * from monkey;'

mysql keeper -u keeper_guest -e 'select * from zoo_keeper;'

# GET
printf "\n\n\ncommand: GET monkeys\n\n" | tee  output.txt  error.txt
curl localhost:5000/monkeys/ >> output.txt 2>> error.txt

printf "\n\n\ncommand: GET zoos\n\n" | tee  -a output.txt  error.txt
curl localhost:5000/zoos/ >> output.txt 2>> error.txt

printf "\n\n\ncommand: GET keepers\n\n" | tee  -a output.txt  error.txt
curl localhost:5000/zoo_keepers/ | jq . >> output.txt 2>> error.txt

printf "\n\n\ncommand: GET keeper name Bob\n\n" | tee  -a output.txt  error.txt
curl localhost:5000/zoo_keepers/1 | jq . >> output.txt 2>> error.txt

printf "\n\n\ncommand: GET keeper  ERROR\n\n" | tee  -a output.txt  error.txt
curl localhost:5000/zoo_keepers/nope >> output.txt 2>> error.txt

# POST
printf "\n\n\ncommand POST keeper \n\n" | tee  -a output.txt  error.txt
curl -H "content-Type: application/json" -X POST -d\
     "{\"name\": \"Nancy\", \"age\": \"100\",      \
     \"zoo_id\": \"2\", \"favorite_monkey\": \"2\"}" \
     localhost:5000/zoo_keepers/ | jq . >> output.txt 2>> error.txt

printf "\n\n\ncommand POST keeper ERROR FAVORITE NOT IN ZOO \n\n" | tee  -a output.txt  error.txt
curl -H "content-Type: application/json" -X POST -d\
     "{\"name\": \"Nancy\", \"age\": \"100\",      \
     \"zoo_id\": \"2\", \"favorite_monkey\": \"1\"}" \
     localhost:5000/zoo_keepers/ >> output.txt 2>> error.txt

# PUT
printf "\n\n\ncommand PUT keeper: FULL \n\n" | tee  -a output.txt  error.txt
curl -H "content-Type: application/json" -X PUT -d\
     "{\"age\": \"200\",      \
     \"zoo_id\": \"1\", \"favorite_monkey\": \"1\"}" \
     localhost:5000/zoo_keepers/4 | jq . >> output.txt 2>> error.txt

printf "\n\n\ncommand PUT keeper: PARTIAL \n\n" | tee  -a output.txt  error.txt
curl -H "content-Type: application/json" -X PUT -d\
     "{\"age\": \"300\",      \
     \"dream_monkey\": \"2\"}" \
     localhost:5000/zoo_keepers/4 | jq . >> output.txt 2>> error.txt

printf "\n\n\ncommand PUT keeper: ERROR \n\n" | tee  -a output.txt  error.txt
curl -H "content-Type: application/json" -X PUT -d\
     "{\"age\": \"500\",      \
     \"dream_monkey\": \"4\"}" \
     localhost:5000/zoo_keepers/4 >> output.txt 2>> error.txt

printf "\n\n\ncommand GET keeper: after ERROR did not change values\n\n" | tee  -a output.txt  error.txt
curl localhost:5000/zoo_keepers/4 | jq . >> output.txt 2>> error.txt


# HEAD

printf "\n\n\ncommand HEAD zoos \n\n" | tee  -a output.txt  error.txt
curl -I localhost:5000/zoos/ >> output.txt 2>> error.txt

printf "\n\n\ncommand HEAD monkeys \n\n" | tee  -a output.txt  error.txt
curl -I localhost:5000/monkeys/ >> output.txt 2>> error.txt

printf "\n\n\ncommand HEAD keepers \n\n" | tee  -a output.txt  error.txt
curl -I localhost:5000/zoo_keepers/ >> output.txt 2>> error.txt

printf "\n\n\ncommand HEAD zoo_keepers/2 \n\n" | tee  -a output.txt  error.txt
curl -I localhost:5000/zoo_keepers/2 >> output.txt 2>> error.txt

printf "\n\n\ncommand HEAD zoo_keepers/Error \n\n" | tee  -a output.txt  error.txt
curl -I localhost:5000/Error >> output.txt 2>> error.txt


# DELETE

printf "\n\n\ncommand delete Joe\n\n" | tee  -a output.txt  error.txt
curl -X DELETE localhost:5000/zoo_keepers/2 | jq . >> output.txt 2>> error.txt

printf "\n\n\ncommand: GET keepers\n\n" | tee  -a output.txt  error.txt
curl localhost:5000/zoo_keepers/ >> output.txt 2>> error.txt
