"""Domain-agnostic helpers for diffing api content by `_id.$oid`.

Shared by the MISSING / NEWS / INVASIONS / FISSURES flows in
`src/cogs/tasks/check_new_content.py`.
"""


def extractID(obj_prev, obj_new):
    return (
        {item["_id"]["$oid"] for item in obj_prev},
        {item["_id"]["$oid"] for item in obj_new},
    )


def checkMissingIds(obj_prev, obj_new):
    """Compare items by _id.$oid.

    Returns:
        (changed, newly_added_ids)
        changed: True if the id sets differ in any way (added OR removed),
                 i.e. the cache should be re-saved.
        newly_added_ids: ids present in obj_new but not in obj_prev.
    """
    prev_ids, new_ids = extractID(obj_prev, obj_new)
    return prev_ids != new_ids, new_ids - prev_ids


def checkMissingItem(obj_new, newly_added_ids):
    """Return the full items from obj_new whose ids are newly added."""
    return [item for item in obj_new if item["_id"]["$oid"] in newly_added_ids]
