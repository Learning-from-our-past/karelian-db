## Database

A db design for _Siirtokarjalaisten tie_ data extracted with Kaira-core. Reads json-dataset generated by Kaira-core and creates
a Postgres database.

## Usage environment

For Windows and MS Access user, check the wiki for configuration guide. Basically you'll need Postgres ODBC drivers
and some configuration to connect to the database.

## Development environment

Following instructions are for Ubuntu but should be exactly same for macOS with exception of how the general dependencies
are installed.

### Postgres in Docker

**NOTE: This should only be used for development, not in production! The `conf.sql` file that is used to tweak the
PostgreSQL configuration contains options intended for use in a development environment.**

1. Install [Docker Community Edition](https://www.docker.com/get-docker)
2. Install Python requirements:
   ```
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. Setup the project with invoke command:
   ```
   invoke docker-db-setup
   ```
   Note that the port used by the Docker DB can be specified with `-p <port>`
4. The end of the setup will prompt you to set your `DB_PORT` environment variable correctly, don't skip this!
5. Operate the DB with `docker-db-start` and `docker-db-stop`

If you completed this step, you may skip down to [Datalinking](#datalinking).

### General dependencies

**NOTE: If you have done the [Postgres in Docker](#postgres-in-docker) step, you may skip all the following setup stuff
and go straight down to [Datalinking](#datalinking). It is advisable to use Docker for development since the
installation process is likely significantly easier.**

- Python >=3.5
- Postgres 9.6.1
- PostGIS bundle for Postgres 9.6
- [PL/Python3](https://www.postgresql.org/docs/9.6/static/plpython.html)
- virtualenv

After installing Postgres and Postgis, on Ubuntu you can install the plpython with:

```
sudo apt-get install -y postgresql-plpython3-9.6
```

### Setup Postgres .pgpass file

Instead of .pgpass file, on your [development] machine you can probably just set local connections as trusted
in your pg_hba configuration. Of course you should consider possible security implications of this.

Set up postgres or other superuser to have a password access and then add following lines to `~/.pgpass`:

```
localhost:5432:postgres:postgres:<password>
localhost:5432:learning-from-our-past:postgres:<password>
localhost:5432:karelian_testdb:postgres:<password>
```

Add similar entry for production connection with correct host and passwords if you want to access the production database.
Set rights of the file to the 0600. [Read more about PGPASSFILE ](https://www.postgresql.org/docs/9.6/static/libpq-pgpass.html)

Create user with name `kaira` to your database cluster. There's a `./sql/roles.sql` file that you can use to set `kaira` (and others) up easily, like so:

```
cat sql/roles.sql | docker exec -i lfop-db-container bash -c 'psql -U postgres -d learning-from-our-past'
docker exec -it lfop-db-container bash -c "psql -U postgres -d learning-from-our-past"
ALTER USER kaira WITH PASSWORD 'your-very-secret-password-here';
```

Then add its credentials to the pgpass:

```
localhost:5432:learning-from-our-past:kaira:<password>
localhost:5432:karelian_testdb:kaira:<password>
```

Finally setup environment variable for your database super user if you want to use separate user from default postgres
user:

```
export DB_ADMIN_NAME=yourname
```

This can be done in `.env` file if you use autoenv or exported however you like.

### Setup the project

After database is setup and dependencies installed, run following commands on the root directory of the project:

```
virtualenv -p python3 database-venv
source database-venv/bin/activate
invoke setup
```

This should setup a new database called `learning-from-our-past` to your local postgres cluster.
Finally run test command to check if all tests pass:

```
invoke test-all
```

If tests pass everything should be fine.

## Datalinking

If you wish to use the datalinking feature, you must have a MySQL database set up on your computer
with the Katiha data imported. For development, MySQL Ver 14.14 Distrib 5.7.21 was used. The default
options expect there to be a user called "kaira" in the MySQL database with access to tables in the
Katiha database. You can achieve this in the MySQL shell with something like:

```sql
CREATE USER 'kaira'@'localhost';  -- you can add IDENTIFIED BY 'password' if a password is desired
GRANT SELECT ON katiha.* TO 'kaira'@'localhost';
```

Once the above criteria are met, you should simply be able to run the following command:

```
inv link-data
```

This will, by default, output the linked data to the material/ directory.

## Autoenv

Autoenv is a handy utility which automatically loads the `.env` file when you cd to the file. See instructions for installation here: https://github.com/kennethreitz/autoenv

## Database monitoring

[Powa](http://dalibo.github.io/powa/) is a simple monitoring tool to inspect the database usage and other stats in browser.
To set up it in your local machine for your local database, follow [Powa docs](http://powa.readthedocs.io/en/latest/powa-web/index.html) about installation.
In short, you'll need to install _PoWA Archivist_ on the machine which has the database.

Once you have installed and configured Powa locally (or you want to use it just for production database), go and rename
file `.powa_template.conf`to `powa-web.conf` in `/database` directory. Then fill in a new random `cookie_secret` and check
that the existing server configurations are ok.

To start POWA gui, run `invoke powa-web` in `/database` directory. Then navigate to [http://localhost:8888](http://localhost:8888)
and log in.
