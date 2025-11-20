TARGET=$rbpi4_remote

DB_NAME=party
CURRENT_DATETIME=$(date "+%y%m%d-%H%M%S")

echo $CURRENT_DATETIME
scp -r $TARGET:wfk/db/$DB_NAME.db backup/db/$DB_NAME-$CURRENT_DATETIME.db
