test:
	cd ..; python -m pytest kairatools

new-migration:
	cd ..; python -m kairatools.tasks.new_migration

migrate:
	cd ..; python -m kairatools.tasks.migrate

create-super-user:
	cd ..; python -m kairatools.tasks.create_superuser

kill-connections-test:
	psql -U postgres -d karelian_testdb -c "SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity WHERE pg_stat_activity.datname = 'karelian_testdb' AND pid <> pg_backend_pid();"
