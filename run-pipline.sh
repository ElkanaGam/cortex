#!/bin/bash

# activate rabbitmq
sudo docker run -d -p 5672:5672 rabbitmq>/dev/null
# run postgres docker
sudo docker run -d -p 5432:5432 -e POSTRGES_USER=postgres -e POSTGRES_PASSWORD=elkana1 postgres>/dev/null
#cretae database 
psql -U postgres -c "CREATE DATABASE mydb;" 
#connect to db
python -m cotrex.saver run-saver  postgresql://127.0.0.1:5432&>/dev/null&
# start parse
python -m cotrex.parsers run-all&>/dev/null&
# start server
python -m cotrex.server run-server -h 127.0.01 -p 8000 rabbitmq://127.0.0.1:5672/
# run api server
python -m cotrex.api run-api-server&>/dev/null&
# run gui server
python cotrex.gui.py&>/dev/null&
