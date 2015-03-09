# migration-rethinkdb-to-mongodb
Internal tool to migrate data from our rethinkdb base to our mongodb database

# Dev Commands
## Run script in docker
    docker build -t "siz-migration-rethinkdb-to-mongodb" .
    docker run --rm --link siz-api-rethinkdb:rethinkdb --link siz-api-mongo:mongo -v $(pwd):/opt/migration-rethinkdb-to-mongodb siz-migration-rethinkdb-to-mongodb
## Access to a mongodb instance through a docker
    docker run --rm -it --link siz-api-mongo:mongo mongo mongo mongo:27017/siz

# Prod commands
## Launch migration job
    docker run -e RETHINKDB_HOST=rethinkdb -e MONGO_AUTH=True -e MONGO_PASSWORD=password --link mongo:mongo sizio/migration-rethinkdb-to-mongodb
## Launch without video conversion
    docker run -e RETHINKDB_HOST=rethinkdb -e MONGO_HOST=mongo_host -e MONGO_AUTH=True -e MONGO_PASSWORD=password -e CONVERT_VIDEO=False sizio/migration-rethinkdb-to-mongodb

# Preprod commands
## Launch migration job
    docker run -e AWS_ACCESS_KEY_ID=AAAAAAAAAAAAAAAAAAAAAA -e AWS_SECRET_ACCESS_KEY=uUGIUhiuHUIHiuhIUhIUHIUhIUhiuhIUhIUhIUHu -e RETHINKDB_HOST=rethinkdb --link mongo:mongo sizio/migration-rethinkdb-to-mongodb