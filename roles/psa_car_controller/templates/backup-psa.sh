BACKUP_SERVER_URL="christian@ds3018:/volume1/backup/psa"
BACKUP_FILE="psa_$(date '+%F_%H-%M').tgz"

cd /home/pi/psa
tar -czf psacc.tgz config

scp psacc.tgz  ${BACKUP_SERVER_URL}/${BACKUP_FILE}

rm psacc.tgz
