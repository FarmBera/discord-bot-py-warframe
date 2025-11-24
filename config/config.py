class Lang:
    EN: str = "en"
    KO: str = "ko"


language = Lang.
# language = input("Select Language (en/ko) >> ")


class LOG_TYPE:
    cmd: str = "cmd"
    event: str = "event"
    err: str = "err"
    cooldown: str = ".cooldown"
    maintenance: str = "maintenance"
    e_event: str = "event.err"
    e_admin: str = "err.admin"
