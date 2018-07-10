hyper service create --env-file "./.test-env" --size S2 --protocol http --service-port 80 --container-port 5000 --name healthworkers-test --label=app=healthworkers-test --replicas 1 nandanrao/healthworkers
sleep 10
hyper service attach-fip --fip=209.177.88.233 healthworkers-test
