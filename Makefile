new-migration:
	python -m tasks.new-migration

migrate:
	python -m tasks.migrate

populate-all:
	sh tasks/populate_everything.sh