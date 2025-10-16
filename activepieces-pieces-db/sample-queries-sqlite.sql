-- Sample SQLite Queries for Activepieces Pieces Database
-- Use these queries to explore and query the database

-- ==============================================
-- BASIC QUERIES
-- ==============================================

-- Count all pieces
SELECT COUNT(*) as total_pieces FROM pieces;

-- Count all actions and triggers
SELECT 
    (SELECT COUNT(*) FROM pieces) as pieces,
    (SELECT COUNT(*) FROM actions) as actions,
    (SELECT COUNT(*) FROM triggers) as triggers,
    (SELECT COUNT(*) FROM action_properties) as action_properties,
    (SELECT COUNT(*) FROM trigger_properties) as trigger_properties;

-- List all pieces
SELECT name, display_name, auth_type FROM pieces ORDER BY display_name LIMIT 20;

-- Get a specific piece
SELECT * FROM pieces WHERE name = 'gmail';

-- ==============================================
-- FULL-TEXT SEARCH (FTS5)
-- ==============================================

-- Search pieces by keyword
SELECT p.name, p.display_name, p.description
FROM pieces_fts
JOIN pieces p ON pieces_fts.rowid = p.id
WHERE pieces_fts MATCH 'email'
ORDER BY rank
LIMIT 10;

-- Search actions by keyword
SELECT 
    p.display_name as piece,
    a.display_name as action,
    a.description
FROM actions_fts
JOIN actions a ON actions_fts.rowid = a.id
JOIN pieces p ON a.piece_id = p.id
WHERE actions_fts MATCH 'send'
ORDER BY rank
LIMIT 20;

-- Complex search with AND operator
SELECT p.display_name, p.description
FROM pieces_fts
JOIN pieces p ON pieces_fts.rowid = p.id
WHERE pieces_fts MATCH 'email AND automation'
LIMIT 10;

-- Search with OR operator
SELECT p.display_name
FROM pieces_fts
JOIN pieces p ON pieces_fts.rowid = p.id
WHERE pieces_fts MATCH 'slack OR discord OR teams'
LIMIT 10;

-- ==============================================
-- PIECES WITH STATISTICS
-- ==============================================

-- Top pieces by action count
SELECT display_name, action_count, trigger_count
FROM piece_statistics
WHERE action_count > 0
ORDER BY action_count DESC
LIMIT 15;

-- Pieces with only triggers (no actions)
SELECT display_name, trigger_count
FROM pieces_with_capabilities
WHERE has_triggers = 1 AND has_actions = 0
ORDER BY trigger_count DESC;

-- Pieces with both actions and triggers
SELECT display_name, action_count, trigger_count
FROM pieces_with_capabilities
WHERE has_actions = 1 AND has_triggers = 1
ORDER BY (action_count + trigger_count) DESC
LIMIT 20;

-- ==============================================
-- ACTIONS
-- ==============================================

-- Get all actions for a piece
SELECT display_name, description, requires_auth
FROM actions
WHERE piece_id = (SELECT id FROM pieces WHERE name = 'gmail')
ORDER BY display_name;

-- Search for actions containing a keyword
SELECT 
    p.display_name as piece,
    a.display_name as action,
    a.description
FROM actions a
JOIN pieces p ON a.piece_id = p.id
WHERE a.display_name LIKE '%send%'
   OR a.description LIKE '%send%'
ORDER BY p.display_name, a.display_name
LIMIT 20;

-- Get action with its properties
SELECT 
    a.display_name as action,
    ap.display_name as property,
    ap.type,
    ap.required,
    ap.description
FROM actions a
LEFT JOIN action_properties ap ON a.id = ap.action_id
WHERE a.piece_id = (SELECT id FROM pieces WHERE name = 'gmail')
  AND a.name = 'send_email'
ORDER BY ap.required DESC, ap.display_name;

-- ==============================================
-- TRIGGERS
-- ==============================================

-- Get all triggers for a piece
SELECT display_name, description, trigger_type, requires_auth
FROM triggers
WHERE piece_id = (SELECT id FROM pieces WHERE name = 'slack')
ORDER BY display_name;

-- All webhook triggers
SELECT 
    p.display_name as piece,
    t.display_name as trigger
FROM triggers t
JOIN pieces p ON t.piece_id = p.id
WHERE t.trigger_type = 'WEBHOOK'
ORDER BY p.display_name;

-- All polling triggers
SELECT 
    p.display_name as piece,
    t.display_name as trigger
FROM triggers t
JOIN pieces p ON t.piece_id = p.id
WHERE t.trigger_type = 'POLLING'
ORDER BY p.display_name;

-- ==============================================
-- PROPERTIES
-- ==============================================

-- Get all properties for an action
SELECT 
    name,
    display_name,
    type,
    required,
    description
FROM action_properties
WHERE action_id = (
    SELECT id FROM actions 
    WHERE name = 'send_email' 
    AND piece_id = (SELECT id FROM pieces WHERE name = 'gmail')
)
ORDER BY required DESC, display_name;

-- Find required properties across all actions
SELECT 
    p.display_name as piece,
    a.display_name as action,
    ap.display_name as property,
    ap.type
FROM action_properties ap
JOIN actions a ON ap.action_id = a.id
JOIN pieces p ON a.piece_id = p.id
WHERE ap.required = 1
ORDER BY p.display_name, a.display_name, ap.display_name
LIMIT 50;

-- Count properties by type
SELECT type, COUNT(*) as count
FROM action_properties
GROUP BY type
ORDER BY count DESC;

-- ==============================================
-- AUTHENTICATION
-- ==============================================

-- Pieces by authentication type
SELECT auth_type, COUNT(*) as count
FROM pieces
WHERE auth_type IS NOT NULL
GROUP BY auth_type
ORDER BY count DESC;

-- OAuth2 pieces
SELECT display_name, description
FROM pieces
WHERE auth_type = 'OAuth2'
ORDER BY display_name;

-- Pieces with no authentication
SELECT display_name
FROM pieces
WHERE auth_type IS NULL OR auth_type = 'none'
ORDER BY display_name
LIMIT 20;

-- ==============================================
-- CATEGORIES
-- ==============================================

-- Note: Categories are stored as JSON text, so we need to use LIKE
SELECT name, display_name, categories
FROM pieces
WHERE categories LIKE '%COMMUNICATION%'
ORDER BY display_name;

-- ==============================================
-- COMPLEX QUERIES
-- ==============================================

-- Complete piece information with counts
SELECT 
    p.name,
    p.display_name,
    p.description,
    p.auth_type,
    COUNT(DISTINCT a.id) as action_count,
    COUNT(DISTINCT t.id) as trigger_count,
    COUNT(DISTINCT ap.id) as property_count
FROM pieces p
LEFT JOIN actions a ON p.id = a.piece_id
LEFT JOIN triggers t ON p.id = t.piece_id
LEFT JOIN action_properties ap ON a.id = ap.action_id
WHERE p.name = 'slack'
GROUP BY p.id;

-- Find pieces with specific action types
SELECT DISTINCT p.display_name
FROM pieces p
JOIN actions a ON p.id = a.piece_id
WHERE a.display_name LIKE '%Send%Message%'
ORDER BY p.display_name;

-- Actions requiring authentication
SELECT 
    p.display_name as piece,
    a.display_name as action,
    p.auth_type
FROM actions a
JOIN pieces p ON a.piece_id = p.id
WHERE a.requires_auth = 1
ORDER BY p.display_name, a.display_name
LIMIT 30;

-- ==============================================
-- EXPORT/ANALYSIS QUERIES
-- ==============================================

-- Export all piece names and URLs (for reference)
SELECT name, display_name, logo_url
FROM pieces
ORDER BY display_name;

-- Get property statistics per piece
SELECT 
    p.display_name,
    COUNT(DISTINCT a.id) as actions,
    COUNT(DISTINCT ap.id) as total_properties,
    SUM(CASE WHEN ap.required = 1 THEN 1 ELSE 0 END) as required_properties
FROM pieces p
LEFT JOIN actions a ON p.id = a.piece_id
LEFT JOIN action_properties ap ON a.id = ap.action_id
GROUP BY p.id, p.display_name
HAVING actions > 0
ORDER BY total_properties DESC
LIMIT 20;

-- Find similar pieces (by common words in description)
SELECT DISTINCT p1.display_name as piece1, p2.display_name as piece2
FROM pieces p1, pieces p2
WHERE p1.id < p2.id
  AND p1.description LIKE '%email%'
  AND p2.description LIKE '%email%'
ORDER BY p1.display_name
LIMIT 20;

-- ==============================================
-- USEFUL FOR AI AGENTS
-- ==============================================

-- Get complete action details including all inputs
SELECT 
    p.name as piece_name,
    p.display_name as piece_display_name,
    a.name as action_name,
    a.display_name as action_display_name,
    a.description as action_description,
    ap.name as input_name,
    ap.display_name as input_display_name,
    ap.type as input_type,
    ap.required as input_required,
    ap.description as input_description
FROM pieces p
JOIN actions a ON p.id = a.piece_id
LEFT JOIN action_properties ap ON a.id = ap.action_id
WHERE p.name = 'gmail' AND a.name = 'send_email'
ORDER BY ap.required DESC, ap.display_name;

-- Search for capabilities (e.g., "send email")
SELECT 
    p.display_name as piece,
    a.display_name as action,
    a.description
FROM actions_fts
JOIN actions a ON actions_fts.rowid = a.id
JOIN pieces p ON a.piece_id = p.id
WHERE actions_fts MATCH 'send email'
ORDER BY rank
LIMIT 10;

-- Find all pieces that can send notifications
SELECT DISTINCT p.display_name, p.description
FROM pieces p
JOIN actions a ON p.id = a.piece_id
WHERE a.display_name LIKE '%send%'
   OR a.display_name LIKE '%notify%'
   OR a.display_name LIKE '%post%'
ORDER BY p.display_name;

