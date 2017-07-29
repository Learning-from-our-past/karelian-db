#!/usr/bin/env bash

dropdb learning-from-our-past -U postgres
createdb learning-from-our-past -U postgres
psql -U postgres -d learning-from-our-past -f sql/initial_db.sql
make migrate-local