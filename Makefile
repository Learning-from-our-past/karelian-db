test:
	python -m pytest

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

kill-connections-test:
	psql -U postgres -d karelian_testdb -c "SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity WHERE pg_stat_activity.datname = 'karelian_testdb' AND pid <> pg_backend_pid();"
