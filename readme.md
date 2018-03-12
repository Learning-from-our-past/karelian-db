## database/
A db design for *Siirtokarjalaisten tie* data extracted with Kaira-core. Reads json-dataset generated by Kaira-core and creates
a Postgres database.

## kairatools/
An online web-interface for data exploration and manual fixing tasks

## Usage environment
For Windows and MS Access user, check the wiki for configuration guide. Basically you'll need Postgres ODBC drivers
and some configuration to connect to the database.

## Development environment
Following instructions are for Ubuntu but should be exactly same for Mac OSX with exception of how the general dependencies
are installed.

### General dependencies
* Python >=3.5
* Postgres 9.6.1
* PostGIS bundle for Postgres 9.6
* [PL/Python3](https://www.postgresql.org/docs/9.6/static/plpython.html) 
* virtualenv

After installing Postgres and Postgis, on Ubuntu you can install the plpython with:
```
sudo apt-get install -y postgresql-plpython3-9.6
```

### Setup Postgres .pgpass file
Instead of .pgpass file, on your development machine you can probably just set local connections as trusted
in your pg_hba configuration. Of course you should consider possible security implications of this.

Set up postgres or other superuser to have a password access and then add following lines to `~/.pgpass`:

```
localhost:5432:postgres:postgres:<password>
localhost:5432:learning-from-our-past:postgres:<password>
localhost:5432:karelian_testdb:postgres:<password>
```

Add similar entry for production connection with correct host and passwords if you want to access the production database. 
Set rights of the file to the 0600. [Read more about PGPASSFILE ](https://www.postgresql.org/docs/9.6/static/libpq-pgpass.html)

Create user with name `kaira` to your database cluster and add its credentials to the pgpass:
```
localhost:5432:learning-from-our-past:kaira:<password>
localhost:5432:karelian_testdb:kaira:<password>
```

Finally setup environment variable for your database super user if you want to use separate user from default postgres
user:
```
export DB_ADMIN_NAME=yourname
```
 
This can be done in `.env` file if you use autoenv (see env configuration for kairatools below) or exported however you like.

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

## Configure .env file for kairatools
Kairatools gets various configurations through environment variables which should be set for development environment. This can
be done via `.env` file. Create a new `.env` file to the root of the project with contents of `env-template` file and fill in 
details suitable for your local environment.

## Autoenv
Autoenv is a handy utility which automatically loads the `.env` file when you cd to the file. See instructions for installation here: https://github.com/kennethreitz/autoenv

## Database monitoring
[Powa](http://dalibo.github.io/powa/) is a simple monitoring tool to inspect the database usage and other stats in browser.
To set up it in your local machine for your local database, follow [Powa docs](http://powa.readthedocs.io/en/latest/powa-web/index.html) about installation.
In short, you'll need to install *PoWA Archivist* on the machine which has the database.

Once you have installed and configured Powa locally (or you want to use it just for production database), go and rename
file `.powa_template.conf`to `powa-web.conf` in `/database` directory. Then fill in a new random `cookie_secret` and check
that the existing server configurations are ok.

To start POWA gui, run `invoke powa-web` in `/database` directory. Then navigate to [http://localhost:8888](http://localhost:8888)
and log in.
