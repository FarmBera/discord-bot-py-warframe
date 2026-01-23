from src.parser.archimedea import (
    getDeepArchimedea,
    CT_LAB,
    getTemporalArchimedea,
    CT_HEX,
)


def handleDeepArchimedea(obj_new):
    obj_new = next(i for i in obj_new if i.get("Type") == CT_LAB)
    is_new = (
        getDeepArchimedea()["Activation"]["$date"]["$numberLong"]
        != obj_new["Activation"]["$date"]["$numberLong"]
    )
    return obj_new, is_new


def handleTemporalArchimedea(obj_new):
    obj_new = next(i for i in obj_new if i.get("Type") == CT_HEX)
    is_new = getTemporalArchimedea()["Activation"]["$date"]["$numberLong"] != (
        obj_new["Activation"]["$date"]["$numberLong"]
    )
    return obj_new, is_new
