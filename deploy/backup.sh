#!/bin/bash
BACKUP_DIR="/backups/mysql"
mkdir -p "$BACKUP_DIR"
mysqldump -u root -p"$MYSQL_ROOT_PASSWORD" llm_platform | gzip > "$BACKUP_DIR/db_$(date +%Y%m%d_%H%M%S).sql.gz"
find "$BACKUP_DIR" -name "db_*.sql.gz" -mtime +30 -delete
