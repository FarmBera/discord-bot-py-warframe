class Lang:
    EN: str = "en"
    KO: str = "ko"


language = Lang.KO
# language = input("Select Language (en/ko) >> ")


class LOG_TYPE:
    debug: str = "debug"
    api: str = "api"
    info: str = "info"
    warn: str = "warn"
    err: str = "err"
    crit: str = "critical"

    cmd: str = "cmd"
    msg: str = "msg"
    event: str = "event"
    unable: str = "unavailable"

    cooldown: str = ".cooldown"
    maintenance: str = "maintenance"
    e_event: str = "event.err"
    e_admin: str = "err.admin"
