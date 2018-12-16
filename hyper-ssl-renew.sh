#!/bin/sh


# hyper service detach-fip healthworkers

# hyper run -it -p "80:80" -p "443:443" --name certbot --volume cert:/etc certbot/certbot certonly --standalone -d healthworkers.nandan.cloud

# hyper fip attach 209.177.93.17 certbot
# hyper run -v cert:/home/nandan --rm ubuntu cat /home/nandan/letsencrypt/archive/healthworkers.nandan.cloud/privkey1.pem > privkey.pem 
# hyper run -v cert:/home/nandan --rm ubuntu cat /home/nandan/letsencrypt/archive/healthworkers.nandan.cloud/fullchain1.pem > fullchain.pem 
