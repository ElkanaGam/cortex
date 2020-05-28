# see running dockers
sudo docker ps
# activate rabbitmq
sudo docker run -d -p 5672:5672 rabbitmq
# kill processes on specific port
sudo kill -9 $(sudo lsof -t -i:<port>)
# run postgres docker
sudo docker run -d -p 5432:5432 -e POSTRGES_USER=postgres -e POSTGRES_PASSWORD=password postgres
# run postgres shell
psql -h 127.0.0.1 -p 5432 -U postgres   #password =*password*
# client
python -m client upload-sample -h 127.0.0.1 -p 8000 ./sample.mind
# server
python -m server run-server -h 127.0.01 -p 8000 rabbitmq://127.0.0.1:5672/
# parsers
python -m parsers run-all
# saver
python -m saver run-saver  postgresql://127.0.0.1:5432

#activeate venv
C:\temp\shared\.env\Scripts\activate.bat

#move to directory
cd ../../temp/shared

#run api server
python -m api run-api-server