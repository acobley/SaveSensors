docker stop mysqldata
docker stop sensorsaver
docker rm mysqldata
docker rm sensorsaver
docker build -t savesensors .
docker tag savesensors acobley/savesensors
docker push acobley/savesensors
docker run --name mysqldata -e MYSQL_ROOT_PASSWORD=dacjd156n. -d mysql:latest
sleep 30
docker run  --name sensorsaver --link mysqldata:mysql acobley/savesensors
