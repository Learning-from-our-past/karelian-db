create-venv:
	virtualenv -p python3 database-venv

setup:
	psql template1 -c 'create extension hstore'; # install hstore extension to default database template
	pip install -r requirements.txt;
	createdb learning-from-our-past
	psql -U postgres -d learning-from-our-past -a -f database/sql/initial_db.sql
	python -m database.tasks.migrate
	python -m kairatools.tasks.migrate

test:
	cd database; make test;
	cd kairatools; make test;
