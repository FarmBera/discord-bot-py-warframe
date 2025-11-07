TARGET=$rbpi4_remote

CURRENT_DATETIME=$(date "+%y%m%d-%H%M%S")

echo $CURRENT_DATETIME
scp -r $TARGET:wfk/db/party.db backup/db/party-$CURRENT_DATETIME.db
