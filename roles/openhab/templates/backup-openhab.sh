
BACKUP_DIR=" /var/lib/openhab/backups"
BACKUP_SERVER_URL="christian@ds3018:/volume1/backup/openhab"

sudo /usr/share/openhab/runtime/bin/backup

BACKUP_FILE=$(/bin/ls -tr ${BACKUP_DIR}/ |tail -1)
scp ${BACKUP_DIR}/${BACKUP_FILE} ${BACKUP_SERVER_URL}/
