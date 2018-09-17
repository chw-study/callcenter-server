hyper service create --env-file ./.env --size S2 --service-port 443 --container-port 5000 --name healthworkers --ssl-cert=ssl.pem --protocol httpsTerm --label=app=healthworkers --replicas 2 nandanrao/healthworkers
sleep 10
hyper service attach-fip --fip=209.177.93.17 healthworkers
