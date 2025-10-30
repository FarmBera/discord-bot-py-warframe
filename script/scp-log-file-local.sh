CURRENT_DATETIME=$(date "+%y%m%d-%H%M")

scp $rbpi4_local:discord-bot-py-warframe/log/log.csv log/log-en-$CURRENT_DATETIME.csv
scp $rbpi4_local:discord-bot-py-warframe-kr/log/log.csv log/log-kr-$CURRENT_DATETIME.csv
