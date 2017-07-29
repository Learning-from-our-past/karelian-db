new-migration:
	python -m tasks.new-migration

migrate-local:
	python -m tasks.migrate

migrate-production:
	python -m tasks.migrate-production

populate-all:
	sh tasks/populate_everything.sh

truncate:
	sh tasks/truncate.sh