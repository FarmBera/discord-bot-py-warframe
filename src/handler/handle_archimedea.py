from src.parser.archimedea import (
    getDeepArchimedea,
    CT_LAB,
    getTemporalArchimedea,
    CT_HEX,
)


def categorize_new(new, key):
    return next(i for i in new if i.get("Type") == key)


def checking_new(prev, new):
    return (
        prev["Activation"]["$date"]["$numberLong"]
        != new["Activation"]["$date"]["$numberLong"]
    )


def handleDeepArchimedea(obj_new):
    obj_new = categorize_new(obj_new, CT_LAB)
    return obj_new, checking_new(getDeepArchimedea(), obj_new)


def handleTemporalArchimedea(obj_new):
    obj_new = categorize_new(obj_new, CT_HEX)
    return obj_new, checking_new(getTemporalArchimedea(), obj_new)
