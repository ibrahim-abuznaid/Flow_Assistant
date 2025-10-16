-- SQLite Schema for Activepieces Pieces Database
-- This is a simplified version optimized for SQLite

-- Enable foreign keys
PRAGMA foreign_keys = ON;

-- Pieces table
CREATE TABLE IF NOT EXISTS pieces (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    display_name TEXT NOT NULL,
    description TEXT,
    logo_url TEXT,
    version TEXT,
    minimum_supported_release TEXT,
    auth_type TEXT,
    categories TEXT, -- JSON array stored as text
    authors TEXT, -- JSON array stored as text
    metadata TEXT, -- JSON object stored as text
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Actions table
CREATE TABLE IF NOT EXISTS actions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    piece_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    display_name TEXT NOT NULL,
    description TEXT,
    requires_auth INTEGER DEFAULT 0, -- SQLite uses INTEGER for boolean (0=false, 1=true)
    metadata TEXT, -- JSON object stored as text
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (piece_id) REFERENCES pieces(id) ON DELETE CASCADE,
    UNIQUE(piece_id, name)
);

-- Triggers table
CREATE TABLE IF NOT EXISTS triggers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    piece_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    display_name TEXT NOT NULL,
    description TEXT,
    trigger_type TEXT,
    requires_auth INTEGER DEFAULT 0, -- SQLite uses INTEGER for boolean
    metadata TEXT, -- JSON object stored as text
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (piece_id) REFERENCES pieces(id) ON DELETE CASCADE,
    UNIQUE(piece_id, name)
);

-- Action properties table
CREATE TABLE IF NOT EXISTS action_properties (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    action_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    display_name TEXT,
    description TEXT,
    type TEXT NOT NULL,
    required INTEGER DEFAULT 0, -- SQLite uses INTEGER for boolean
    default_value TEXT,
    metadata TEXT, -- JSON object stored as text
    FOREIGN KEY (action_id) REFERENCES actions(id) ON DELETE CASCADE
);

-- Trigger properties table
CREATE TABLE IF NOT EXISTS trigger_properties (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trigger_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    display_name TEXT,
    description TEXT,
    type TEXT NOT NULL,
    required INTEGER DEFAULT 0, -- SQLite uses INTEGER for boolean
    default_value TEXT,
    metadata TEXT, -- JSON object stored as text
    FOREIGN KEY (trigger_id) REFERENCES triggers(id) ON DELETE CASCADE
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_pieces_name ON pieces(name);
CREATE INDEX IF NOT EXISTS idx_actions_piece_id ON actions(piece_id);
CREATE INDEX IF NOT EXISTS idx_actions_name ON actions(name);
CREATE INDEX IF NOT EXISTS idx_triggers_piece_id ON triggers(piece_id);
CREATE INDEX IF NOT EXISTS idx_triggers_name ON triggers(name);
CREATE INDEX IF NOT EXISTS idx_action_properties_action_id ON action_properties(action_id);
CREATE INDEX IF NOT EXISTS idx_trigger_properties_trigger_id ON trigger_properties(trigger_id);

-- Full-text search virtual tables (FTS5)
CREATE VIRTUAL TABLE IF NOT EXISTS pieces_fts USING fts5(
    name,
    display_name,
    description,
    content='pieces',
    content_rowid='id'
);

CREATE VIRTUAL TABLE IF NOT EXISTS actions_fts USING fts5(
    name,
    display_name,
    description,
    content='actions',
    content_rowid='id'
);

CREATE VIRTUAL TABLE IF NOT EXISTS triggers_fts USING fts5(
    name,
    display_name,
    description,
    content='triggers',
    content_rowid='id'
);

-- Triggers to keep FTS tables in sync
CREATE TRIGGER IF NOT EXISTS pieces_ai AFTER INSERT ON pieces BEGIN
    INSERT INTO pieces_fts(rowid, name, display_name, description)
    VALUES (new.id, new.name, new.display_name, new.description);
END;

CREATE TRIGGER IF NOT EXISTS pieces_ad AFTER DELETE ON pieces BEGIN
    DELETE FROM pieces_fts WHERE rowid = old.id;
END;

CREATE TRIGGER IF NOT EXISTS pieces_au AFTER UPDATE ON pieces BEGIN
    UPDATE pieces_fts SET name = new.name, display_name = new.display_name, description = new.description
    WHERE rowid = new.id;
END;

CREATE TRIGGER IF NOT EXISTS actions_ai AFTER INSERT ON actions BEGIN
    INSERT INTO actions_fts(rowid, name, display_name, description)
    VALUES (new.id, new.name, new.display_name, new.description);
END;

CREATE TRIGGER IF NOT EXISTS actions_ad AFTER DELETE ON actions BEGIN
    DELETE FROM actions_fts WHERE rowid = old.id;
END;

CREATE TRIGGER IF NOT EXISTS actions_au AFTER UPDATE ON actions BEGIN
    UPDATE actions_fts SET name = new.name, display_name = new.display_name, description = new.description
    WHERE rowid = new.id;
END;

CREATE TRIGGER IF NOT EXISTS triggers_ai AFTER INSERT ON triggers BEGIN
    INSERT INTO triggers_fts(rowid, name, display_name, description)
    VALUES (new.id, new.name, new.display_name, new.description);
END;

CREATE TRIGGER IF NOT EXISTS triggers_ad AFTER DELETE ON triggers BEGIN
    DELETE FROM triggers_fts WHERE rowid = old.id;
END;

CREATE TRIGGER IF NOT EXISTS triggers_au AFTER UPDATE ON triggers BEGIN
    UPDATE triggers_fts SET name = new.name, display_name = new.display_name, description = new.description
    WHERE rowid = new.id;
END;

-- Views
CREATE VIEW IF NOT EXISTS piece_statistics AS
SELECT 
    p.id,
    p.name,
    p.display_name,
    COUNT(DISTINCT a.id) as action_count,
    COUNT(DISTINCT t.id) as trigger_count,
    COUNT(DISTINCT ap.id) as action_property_count,
    COUNT(DISTINCT tp.id) as trigger_property_count
FROM pieces p
LEFT JOIN actions a ON p.id = a.piece_id
LEFT JOIN triggers t ON p.id = t.piece_id
LEFT JOIN action_properties ap ON a.id = ap.action_id
LEFT JOIN trigger_properties tp ON t.id = tp.trigger_id
GROUP BY p.id, p.name, p.display_name;

CREATE VIEW IF NOT EXISTS pieces_with_capabilities AS
SELECT 
    p.*,
    (SELECT COUNT(*) FROM actions WHERE piece_id = p.id) as action_count,
    (SELECT COUNT(*) FROM triggers WHERE piece_id = p.id) as trigger_count,
    CASE 
        WHEN (SELECT COUNT(*) FROM actions WHERE piece_id = p.id) > 0 THEN 1 
        ELSE 0 
    END as has_actions,
    CASE 
        WHEN (SELECT COUNT(*) FROM triggers WHERE piece_id = p.id) > 0 THEN 1 
        ELSE 0 
    END as has_triggers
FROM pieces p;

