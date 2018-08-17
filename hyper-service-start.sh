hyper service create --env-file "./.env" --size S2 --protocol http --service-port 80 --container-port 5000 --name healthworkers --label=app=healthworkers --replicas 2 nandanrao/hw-server
sleep 10
hyper service attach-fip --fip=209.177.93.17 healthworkers
