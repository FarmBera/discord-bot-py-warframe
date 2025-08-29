def _check_void_trader_update(prev, new):
    """Checks for updates regardless of the data structure (dict or list) of voidTraders."""
    prev_data = prev[-1] if isinstance(prev, list) and prev else prev
    new_data = new[-1] if isinstance(new, list) and new else new
    if not isinstance(prev_data, dict) or not isinstance(new_data, dict):
        # perform a simple comparison. data structure is diff than normal
        return prev != new

    return (prev_data.get("activation"), prev_data.get("active")) != (
        new_data.get("activation"),
        new_data.get("active"),
    )