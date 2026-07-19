#!/bin/bash
if [ -z "$1" ]; then echo "Usage: $0 <backup_file.sql.gz>"; exit 1; fi
gunzip < "$1" | mysql -u root -p"$MYSQL_ROOT_PASSWORD" llm_platform
echo "Restore complete"
