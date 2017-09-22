# Generate ssl keys
openssl req -x509 -nodes -days 1000000 -newkey rsa:4096 -keyout backup_key.pem\
 -subj "/C=FI/ST=Uusimaa/L=Helsinki/O=IT/CN=www.example.com" \
 -out backup_key.pem.pub

# Dump database in custom format to encrypted file
pg_dump -h localhost -d learning-from-our-past -U postgres --format=c | openssl smime -encrypt -aes256 -binary -outform DEM -out learning-from-our-past-dump.ssl ./backup_key.pem.pub

# Decrypt to a file using private key
openssl smime -decrypt -in learning-from-our-past.ssl -binary -inform DEM -inkey backup_key.pem -out learning-from-our-past-dump

# Restore
pg_restore -U postgres -c --if-exists -d learning-from-our-past learning-from-our-past-dump
