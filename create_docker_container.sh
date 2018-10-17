#!/usr/bin/env bash
echo docker stop zoo_keeper_server1
docker stop zoo_keeper_server1
echo docker rm zoo_keeper_server1
docker rm zoo_keeper_server1
echo docker run --network=zoo_network --name=zoo_keeper_server1 --env-file=./docker_env.txt -p 5000:5000 -d zoo_keeper_server
docker run --network=zoo_network --name=zoo_keeper_server1 --env-file=./docker_env.txt -p 5000:5000 -d zoo_keeper_server

