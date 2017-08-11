#!/usr/bin/env bash
psql -U postgres -d learning-from-our-past -c "SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity WHERE pg_stat_activity.datname = 'learning-from-our-past' AND pid <> pg_backend_pid();"
dropdb learning-from-our-past -U postgres
createdb learning-from-our-past -U postgres
psql -U postgres -d learning-from-our-past -f sql/initial_db.sql
make migrate-local