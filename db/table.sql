use dbot_test;

-- Tables
CREATE TABLE IF NOT EXISTS party (
    id INTEGER NOT NULL AUTO_INCREMENT,
    thread_id BIGINT UNIQUE,
    message_id BIGINT UNIQUE,
    host_id BIGINT,
    title TEXT,
    game_name TEXT,
    max_users INTEGER,
    description TEXT,
    status VARCHAR(20) DEFAULT '모집 중',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id)
) DEFAULT CHARACTER SET = 'utf8mb4';

CREATE TABLE IF NOT EXISTS participants (
    party_id INTEGER,
    user_id BIGINT,
    user_mention TEXT,
    display_name TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (party_id, user_id),
    FOREIGN KEY (party_id) REFERENCES party (id) ON DELETE CASCADE
) DEFAULT CHARACTER SET = 'utf8mb4';

CREATE TABLE IF NOT EXISTS trades (
    id INTEGER NOT NULL AUTO_INCREMENT,
    host_id BIGINT NOT NULL,
    game_nickname TEXT NOT NULL,
    trade_type VARCHAR(10) NOT NULL, -- sell, buy
    item_name TEXT NOT NULL,
    item_rank INTEGER NOT NULL DEFAULT 0,
    quantity INTEGER NOT NULL,
    price INTEGER NOT NULL,
    thread_id BIGINT,
    message_id BIGINT,
    status VARCHAR(20) DEFAULT 'open', -- open, closed
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id)
) DEFAULT CHARACTER SET = 'utf8mb4';

/*
경고를 줄 때마다 새로운 기록이 쌓이도록 (경고 이력 테이블)
언제, 무슨 이유(note)로 경고를 받았는지 각각 기록
이 사람의 경고가 몇 회인지를 알기 위해 COUNT(*) 사용
*/
CREATE TABLE IF NOT EXISTS user_warnings (
    id INTEGER NOT NULL AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    display_name VARCHAR(50) NOT NULL,
    is_ban BOOLEAN NOT NULL,
    category VARCHAR(20) NOT NULL,
    note VARCHAR(150),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id)
) DEFAULT CHARACTER SET = 'utf8mb4';

CREATE TABLE IF NOT EXISTS admins (
    id INT NOT NULL AUTO_INCREMENT,
    is_dm_target BOOLEAN NOT NULL DEFAULT FALSE,
    user_id BIGINT NOT NULL UNIQUE,
    note VARCHAR(150),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id)
) DEFAULT CHARACTER SET = 'utf8mb4';