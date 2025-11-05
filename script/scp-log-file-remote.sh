CURRENT_DATETIME=$(date "+%y%m%d-%H%M")

mkdir log/remote/$CURRENT_DATETIME

scp $rbpi4_remote:wf/log/log.csv log/remote/$CURRENT_DATETIME/log-en.csv
scp $rbpi4_remote:wfk/log/log.csv log/remote/$CURRENT_DATETIME/log-kr.csv
