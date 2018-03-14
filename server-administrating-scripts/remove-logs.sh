#!/bin/bash
log_dir="/data/postgresql/9.6/main/pg_log/"
number_of_days=7

find ${log_dir} -type f -prune -mtime \
    +${number_of_days} -exec rm -f {} \;