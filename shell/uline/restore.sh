#!/bin/bash

curr_date=20171223
docker_name=spd_uline_$curr_date
backup_dir=/home/ubuntu/uline_db 
pgdata=/home/ubuntu/pg_data/$curr_date    
docker run -v $pgdata:/var/lib/postgresql/data -v $backup_dir:/backup --name $docker_name  -e POSTGRES_PASSWORD=uline2015 -d postgres:9.6        
sleep 10
docker exec $docker_name /bin/sh -c 'createdb spd_uline -E UTF8 -e -U postgres'
docker exec $docker_name /bin/sh -c 'createdb spd_uline_trade -E UTF8 -e -U postgres'

echo "Restoring uline"
echo "docker exec $docker_name /bin/sh -c 'pg_restore -j 8 --format=d -C -d spd_uline -U postgres -O /backup/spd_uline_$curr_date'"
docker exec $docker_name /bin/sh -c "pg_restore -j 8 --format=d -C -d spd_uline -U postgres -O /backup/spd_uline_$curr_date"

echo "Restoring uline trade"
echo "docker exec $docker_name /bin/sh -c 'pg_restore -j 8 --format=d -C -d spd_uline_trade -U postgres -O /backup/spd_uline_trade_$curr_date'" 
docker exec $docker_name /bin/sh -c "pg_restore -j 8 --format=d -C -d spd_uline_trade -U postgres -O /backup/spd_uline_trade_$curr_date"
echo "Done" 

