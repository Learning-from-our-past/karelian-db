test:
	export APP_SETTINGS=testing; cd ../..; python -m pytest kairatools/backend

new-migration:
	cd ../..; python -m kairatools.backend.tasks.new_migration

migrate:
	cd ../..; python -m kairatools.backend.tasks.migrate

create-super-user:
	cd ../..; python -m kairatools.backend.tasks.create_superuser

kill-connections-test:
	psql -U postgres -d karelian_testdb -c "SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity WHERE pg_stat_activity.datname = 'karelian_testdb' AND pid <> pg_backend_pid();"
