def handleVoidTrader(obj_prev, obj_new):
    prev_data = obj_prev[-1] if isinstance(obj_prev, list) and obj_prev else obj_prev
    new_data = obj_new[-1] if isinstance(obj_new, list) and obj_new else obj_new
    events: list = []

    # 1. is new baro scheduled (check new baro)
    if prev_data.get("Activation") != new_data.get("Activation"):
        events.append(
            {
                "text_key": "cmd.void-traders.baro-new",
                "embed_color": 0xFFDD00,
                "have_custom_msg": False,
            }
        )

    # 2. check exist baro activated
    if not prev_data.get("Manifest") and new_data.get("Manifest"):
        events.append(
            {
                "text_key": "cmd.void-traders.baro-appear",
                "embed_color": None,
                "have_custom_msg": True,
            }
        )

    return events
