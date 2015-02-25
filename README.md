# migration-rethinkdb-to-mongodb
Internal tool to migrate data from our rethinkdb base to our mongodb database

# Commands
## Run script in docker
    docker build -t "siz-migration-rethinkdb-to-mongodb" .
    docker run --rm --link siz-api-rethinkdb:rethinkdb --link siz-api-mongo:mongo -v $(pwd):/opt/migration-rethinkdb-to-mongodb siz-migration-rethinkdb-to-mongodb
## Access to a mongodb instance through a docker
     docker run --rm -it --link siz-api-mongo:mongo mongo mongo mongo:27017/siz