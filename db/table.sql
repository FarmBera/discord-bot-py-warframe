-- Tables
CREATE TABLE IF NOT EXISTS party (
    id INTEGER NOT NULL AUTO_INCREMENT,
    thread_id BIGINT UNIQUE,
    message_id BIGINT UNIQUE,
    host_id BIGINT,
    title TEXT,
    game_name TEXT,
    departure TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
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

CREATE TABLE IF NOT EXISTS trade (
    id INTEGER NOT NULL AUTO_INCREMENT,
    host_id BIGINT NOT NULL,
    game_nickname TEXT NOT NULL,
    trade_type VARCHAR(10) NOT NULL, -- sell, buy
    item_name TEXT NOT NULL,
    item_rank INTEGER NOT NULL DEFAULT 0,
    quantity INTEGER NOT NULL,
    price INTEGER NOT NULL,
    thread_id BIGINT UNIQUE,
    message_id BIGINT UNIQUE,
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
CREATE TABLE IF NOT EXISTS warnings (
    id INTEGER NOT NULL AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    display_name VARCHAR(100) NOT NULL, -- 경고 당시 닉네임 기록 (스냅샷 용도)
    game_nickname VARCHAR(150) NOT NULL,
    category VARCHAR(20) NOT NULL, -- 예: '욕설', '도배' 등
    note VARCHAR(500), -- 사유 상세
    banned BOOLEAN DEFAULT FALSE, -- 이 경고로 인해 밴 처리가 되었는지 여부
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    INDEX idx_user_id (user_id) -- user_id 기준 조회를 빠르게 하기 위한 인덱스
) DEFAULT CHARACTER SET = 'utf8mb4';

CREATE TABLE IF NOT EXISTS admins (
    -- id INT NOT NULL AUTO_INCREMENT,
    user_id BIGINT NOT NULL UNIQUE,
    note VARCHAR(150),
    is_dm_target BOOLEAN NOT NULL DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id)
) DEFAULT CHARACTER SET = 'utf8mb4';

CREATE TABLE IF NOT EXISTS vari (
    name VARCHAR(100) NOT NULL UNIQUE,
    value VARCHAR(300) NOT NULL,
    note VARCHAR(255),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (name)
) DEFAULT CHARACTER SET = 'utf8mb4';

CREATE TABLE IF NOT EXISTS webhooks (
    channel_id BIGINT NOT NULL,
    guild_id BIGINT NOT NULL,
    webhook_url TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    -- notification flags (1: ON, 0: OFF)
    sub_alerts BOOLEAN DEFAULT 0, -- 얼럿 미션
    sub_news BOOLEAN DEFAULT 0, -- 워프레임 뉴스
    sub_sortie BOOLEAN DEFAULT 0, -- 출격
    sub_archonhunt BOOLEAN DEFAULT 0, -- 집정관
    sub_voidtraders BOOLEAN DEFAULT 0, -- 바로 키 티어
    sub_steelpath BOOLEAN DEFAULT 0, -- 스틸에센스
    sub_darchimedea BOOLEAN DEFAULT 0, -- 심층
    sub_tarchimedea BOOLEAN DEFAULT 0, -- 템포럴
    sub_calendar BOOLEAN DEFAULT 0, -- 1999달력
    sub_dailydeals BOOLEAN DEFAULT 0, -- 일일 특가
    sub_invasions BOOLEAN DEFAULT 0, -- 침공
    sub_duviri_wf BOOLEAN DEFAULT 0, -- 두비리 순환로
    sub_duviri_inc BOOLEAN DEFAULT 0, -- 두비리 순환로
    sub_events BOOLEAN DEFAULT 0, -- 이벤트
    PRIMARY KEY (channel_id)
);