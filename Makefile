create-venv:
	virtualenv -p python3 database-venv

recreate-db:
	dropdb -U postgres learning-from-our-past
	createdb -U postgres learning-from-our-past
	psql -U postgres -d learning-from-our-past -a -f database/sql/initial_db.sql
	python -m database.tasks.migrate
	python -m kairatools.backend.tasks.migrate

restore-backup:
	python -m database.tasks.restore_database
