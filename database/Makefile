truncate:
	cd ..; sh database/tasks/truncate.sh

kill-connections-test:
	psql -U postgres -d karelian_testdb -c "SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity WHERE pg_stat_activity.datname = 'karelian_testdb' AND pid <> pg_backend_pid();"

powa-web:
	powa-web --config=.powa-web.conf

purge-pyc:
	find . -name "*.pyc" -exec rm -f {} \;
