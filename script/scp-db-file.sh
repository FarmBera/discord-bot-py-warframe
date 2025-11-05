CURRENT_DATETIME=$(date "+%y%m%d-%H%M%S")

echo $CURRENT_DATETIME
scp -r $rbpi4_local:discord-bot-py-warframe-kr/db backup/db/db-$CURRENT_DATETIME
