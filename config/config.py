class Lang:
    EN: str = "en"
    KO: str = "ko"


language = Lang.
# language = input("Select Language (en/ko) >> ")


class LOG_TYPE:
    cmd: str = "cmd"
    info: str = "info"
    event: str = "event"
    warn: str = "warn"
    err: str = "err"
    cooldown: str = ".cooldown"
    maintenance: str = "maintenance"
    unable: str = "unavailable"
    e_event: str = "event.err"
    e_admin: str = "err.admin"
