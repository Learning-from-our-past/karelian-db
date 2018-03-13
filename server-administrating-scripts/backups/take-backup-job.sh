#!/bin/bash
# #######################
# Modified from the script here: https://www.imagescape.com/blog/2015/12/18/encrypted-postgres-backups/
#
# Postgresql database backup script.
# - this runs out of the postgres user's crontab
# - this runs once per day
# - this takes a database name as the first argument
# - takes dump in postgres custom format
# - this encrypts the dump with aes 256
#
# To extract:
# You need the private key associated with the
# public key defined by the backup_public_key variable.
#
#   openssl smime -decrypt -in learning-from-our-past.ssl -binary -inform SMIME -inkey backup_key.pem -out learning-from-our-past-dump
#
# #######################

# Database Name
database_name="$1"

backup_public_key="/data/backups/backup_key.pem.pub"

# Location to place backups.
backup_dir="/data/backups/learning-from-our-past/"

# Schemas to backup. Only data tables should be backed up to avoid problems with extensions on restore.
backup_schemas="-n siirtokarjalaisten_tie -n system"

# Numbers of days you want to keep copies of your databases
number_of_days=30

if [ -z ${database_name} ]
then
 echo "Please specify a database name as the first argument"
 exit 1
fi

# String to append to the name of the backup files
backup_date=`date +%Y-%m-%d-%H-%M-%S`

# echo "Dumping ${database_name} to ${backup_dir}${database_name}\_${backup_date}.enc"
pg_dump -U postgres -d ${database_name} --format=c ${backup_schemas} | openssl smime -encrypt \
 -aes256 -binary -outform SMIME \
 -out ${backup_dir}${database_name}\_${backup_date}.enc \
 "${backup_public_key}"

find ${backup_dir} -type f -prune -mtime \
    +${number_of_days} -exec rm -f {} \;
