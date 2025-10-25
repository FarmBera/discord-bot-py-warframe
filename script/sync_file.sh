OPTIONS="-rlptvuh --progress --bwlimit=35m --delete"
SOURCE_BASE="$HOME/path/to/your/local/project"
TARGET_PROJECTS=(
    "project-name-1"
    "project-name-another-language"
)

for project in "${TARGET_PROJECTS[@]}"; do
    echo "--- Syncing to $project ---"

    # destination path
    DEST_PATH="remote:/path/to/your/remote/destination"

    # run rsync command
    rsync $OPTIONS "$SOURCE_BASE/docs" "$DEST_PATH/"
    rsync $OPTIONS "$SOURCE_BASE/config/TOKEN.py" "$DEST_PATH/config/"
    rsync $OPTIONS "$SOURCE_BASE/data/" "$DEST_PATH/data/"

    echo ""
done

echo "--- All sync tasks completed. ---"
