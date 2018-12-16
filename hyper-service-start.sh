hyper service create --env-file ./.env --size S2 --protocol httpsTerm --ssl-cert ssl.pem --service-port 443 --container-port 5000 --name healthworkers --label=app=healthworkers --replicas 2 nandanrao/hw-server
sleep 10
hyper service attach-fip --fip=209.177.93.17 healthworkers
