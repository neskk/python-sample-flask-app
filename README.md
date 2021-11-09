# Python Flask App

**This application is just a template meant to help bootstrap python projects.**

## Feature Support

- Flask webserver
- Logging and workspace setup
- Command-line args and configuration parsing
- Multi-threaded work
- MySQL database for data persistence
- Peewee ORM routines for verifying, creating and migrating the schema
- Docker container configuration included

## Useful developer resources

- [ConfigArgParse](https://github.com/bw2/ConfigArgParse)
- [Peewee ORM](http://docs.peewee-orm.com/en/latest/)
- [Python Requests](https://requests.readthedocs.io/en/master/)
- [urllib3](https://urllib3.readthedocs.io/en/latest/)
- [urllib3 - set max retries](https://stackoverflow.com/questions/15431044/can-i-set-max-retries-for-requests-request)
- [Conversion from IP string to integer and backwards](https://stackoverflow.com/a/13294427)
- [Coerce INET_ATON](https://github.com/coleifer/peewee/issues/342)
- [Flask](https://flask.palletsprojects.com/en/2.0.x/)
- [Jinja2](https://jinja2docs.readthedocs.io/en/stable/)

## Usage

- Docker configuration is done through [.env](.env) and ConfigArgParse will prioritize environment variables over config.ini variables.
- Replace all occurrences of `flask_app` with your application module name. **Do not forget to rename the module folder `flask_app` as well**.
- Update [app/requirements.txt](app/requirements.txt) with your project's dependencies.
- Check the usage for existing arguments: `python webserver.py -h`.
- Access the website on [localhost:5000](http://localhost:5000/).

```
usage: start.py [-h] [-cf CONFIG] [-v] [--log-path LOG_PATH] [--download-path DOWNLOAD_PATH] --db-name DB_NAME --db-user DB_USER --db-pass DB_PASS [--db-host DB_HOST] [--db-port DB_PORT]
                [-mc MAX_CONCURRENCY] [-ni NOTICE_INTERVAL] [-p {http,socks,all}]

optional arguments:
  -h, --help            show this help message and exit
  -cf CONFIG, --config CONFIG
                        Set configuration file.
  -v, --verbose         Run in the verbose mode.
  --log-path LOG_PATH   Directory where log files are saved.
  --download-path DOWNLOAD_PATH
                        Directory where download files are saved.

Database:
  --db-name DB_NAME     Name of the database to be used. [env var: MYSQL_DATABASE]
  --db-user DB_USER     Username for the database. [env var: MYSQL_USER]
  --db-pass DB_PASS     Password for the database. [env var: MYSQL_PASSWORD]
  --db-host DB_HOST     IP or hostname for the database. [env var: MYSQL_HOST]
  --db-port DB_PORT     Port for the database. [env var: MYSQL_PORT]

Worker:
  -mc MAX_CONCURRENCY, --max-concurrency MAX_CONCURRENCY
                        Maximum concurrent worker threads. Default: 100.
  -ni NOTICE_INTERVAL, --notice-interval NOTICE_INTERVAL
                        Print manager statistics every X seconds. Default: 60.
  -p {http,socks,all}, --protocol {http,socks,all}
                        Specify the protocol we are using. Default: socks.

Args that start with '--' (eg. -v) can also be set in a config file (app\config\config.ini or specified via -cf).
Config file syntax allows: key=value, flag=true, stuff=[a,b,c]
(for details, see syntax at https://goo.gl/R74nmi).
If an arg is specified in more than one place, then command-line values override environment variables which override config file values which override defaults.
```


## Debugging with VS Code while using Docker containers

1. Launch the containers with the task: `up-debug`
2. Attach to the container using the launch config: `Python: Remote Attach`
3. You should be able to debug, add breakpoints, etc.

### Sources

- Customize the Docker extension: https://code.visualstudio.com/docs/containers/reference
- Debug containerized apps: https://code.visualstudio.com/docs/containers/debug-common
- Use Docker Compose: https://code.visualstudio.com/docs/containers/docker-compose
- Debug Python within a container: https://code.visualstudio.com/docs/containers/debug-python

### tasks.json:

```json
{
    "label": "up-debug",
    "type": "docker-compose",
    "dockerCompose": {
        "up": {
            "detached": true,
            "build": true,
        },
        "files": [
            "${workspaceFolder}/docker-compose.yml",
            "${workspaceFolder}/docker-compose.debug.yml"
        ]
    }
},
{
    "label": "up-database",
    "type": "docker-compose",
    "dockerCompose": {
        "up": {
            "detached": true,
            "build": true,
            "services": ["db"]
        },
        "files": [
            "${workspaceFolder}/docker-compose.yml",
            "${workspaceFolder}/docker-compose.debug.yml"
        ]
    }
}
```

### launch.json

```json
{
    "name": "Python: Remote Attach",
    "type": "python",
    "request": "attach",
    "connect": {
        "host": "localhost",
        "port": 5678
    },
    "pathMappings": [
        {
            "localRoot": "${workspaceFolder}/app",
            "remoteRoot": "/usr/src/app"
        }
    ]
}
```
