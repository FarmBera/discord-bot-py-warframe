CREATE_TABLE_PARTY: str = f"""
CREATE TABLE IF NOT EXISTS party (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    thread_id INTEGER UNIQUE,
    message_id INTEGER UNIQUE,
    host_id INTEGER,
    title TEXT,
    mission_type TEXT,
    max_users INTEGER,
    description TEXT,
    game_nickname TEXT,
    status TEXT DEFAULT '모집 중',
    created_at TIMESTAMP DEFAULT (datetime('now', 'localtime')),
    updated_at TIMESTAMP DEFAULT (datetime('now', 'localtime'))
);
"""

CREATE_TABLE_PARTICIPANTS: str = f"""
CREATE TABLE IF NOT EXISTS participants (
    party_id INTEGER,
    user_id INTEGER,
    user_mention TEXT,
    display_name TEXT,
    created_at TIMESTAMP DEFAULT (datetime('now', 'localtime')),
    updated_at TIMESTAMP DEFAULT (datetime('now', 'localtime')),
    PRIMARY KEY (party_id, user_id),
    FOREIGN KEY (party_id) REFERENCES party (id) ON DELETE CASCADE
);
"""

CREATE_TABLE_TRADES: str = f"""
CREATE TABLE IF NOT EXISTS trades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    host_id INTEGER NOT NULL,
    game_nickname TEXT NOT NULL,
    trade_type TEXT NOT NULL, -- 'sell' or 'buy'
    item_name TEXT NOT NULL,
    item_rank INTEGER NOT NULL DEFAULT 0,
    quantity INTEGER NOT NULL,
    price INTEGER NOT NULL,
    thread_id INTEGER,
    message_id INTEGER,
    status TEXT DEFAULT 'open', -- 'open', 'closed'
    created_at TIMESTAMP DEFAULT (datetime('now', 'localtime')),
    updated_at TIMESTAMP DEFAULT (datetime('now', 'localtime'))
);
"""

CREATE_TRIGGER_PARTY: str = f"""
CREATE TRIGGER IF NOT EXISTS update_party_updated_at
AFTER UPDATE ON party
FOR EACH ROW
BEGIN
    UPDATE party SET updated_at = (datetime('now', 'localtime')) WHERE id = OLD.id;
END;
"""

CREATE_TRIGGER_PARTICIPANTS: str = f"""
CREATE TRIGGER IF NOT EXISTS update_participants_updated_at
AFTER UPDATE ON participants
FOR EACH ROW
BEGIN
    UPDATE participants SET updated_at = (datetime('now', 'localtime')) WHERE party_id = OLD.party_id AND user_id = OLD.user_id;
END;
"""

CREATE_TRIGGER_TRADES: str = f"""
CREATE TRIGGER IF NOT EXISTS update_trades_updated_at
AFTER UPDATE ON trades
FOR EACH ROW
BEGIN
    UPDATE trades SET updated_at = (datetime('now', 'localtime')) WHERE id = OLD.id;
END;
"""
