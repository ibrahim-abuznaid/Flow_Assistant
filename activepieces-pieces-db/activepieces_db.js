/**
 * Activepieces SQLite Database Helper
 * Standalone module for querying Activepieces pieces database.
 * 
 * Usage:
 *   const ActivepiecesDB = require('./activepieces_db');
 *   
 *   const db = new ActivepiecesDB();
 *   await db.connect();
 *   const pieces = await db.searchPieces('email');
 *   console.log(pieces);
 *   await db.close();
 */

const sqlite3 = require('sqlite3');
const { open } = require('sqlite');
const path = require('path');
const fs = require('fs');

class ActivepiecesDB {
  /**
   * Create a new ActivepiecesDB instance
   * @param {string} dbPath - Path to SQLite database. If null, uses 'activepieces-pieces.db' in same directory.
   */
  constructor(dbPath = null) {
    if (dbPath === null) {
      // Default to database in same directory as this script
      dbPath = path.join(__dirname, 'activepieces-pieces.db');
    }
    
    if (!fs.existsSync(dbPath)) {
      throw new Error(`Database file not found: ${dbPath}`);
    }
    
    this.dbPath = dbPath;
    this.db = null;
  }

  /**
   * Connect to the database
   */
  async connect() {
    this.db = await open({
      filename: this.dbPath,
      driver: sqlite3.Database
    });
  }

  /**
   * Close database connection
   */
  async close() {
    if (this.db) {
      await this.db.close();
    }
  }

  /**
   * Search pieces using full-text search
   * @param {string} query - Search query (e.g., 'email', 'slack OR discord')
   * @param {number} limit - Maximum number of results
   * @returns {Promise<Array>} List of matching pieces
   */
  async searchPieces(query, limit = 10) {
    return await this.db.all(`
      SELECT 
        p.name,
        p.display_name,
        p.description,
        p.auth_type,
        (SELECT COUNT(*) FROM actions WHERE piece_id = p.id) as action_count,
        (SELECT COUNT(*) FROM triggers WHERE piece_id = p.id) as trigger_count
      FROM pieces_fts
      JOIN pieces p ON pieces_fts.rowid = p.id
      WHERE pieces_fts MATCH ?
      LIMIT ?
    `, [query, limit]);
  }

  /**
   * Search actions using full-text search
   * @param {string} query - Search query (e.g., 'send email', 'create task')
   * @param {number} limit - Maximum number of results
   * @returns {Promise<Array>} List of matching actions
   */
  async searchActions(query, limit = 10) {
    return await this.db.all(`
      SELECT 
        p.name as piece_name,
        p.display_name as piece_display_name,
        a.name as action_name,
        a.display_name as action_display_name,
        a.description,
        a.requires_auth
      FROM actions_fts
      JOIN actions a ON actions_fts.rowid = a.id
      JOIN pieces p ON a.piece_id = p.id
      WHERE actions_fts MATCH ?
      LIMIT ?
    `, [query, limit]);
  }

  /**
   * Get complete details for a specific piece
   * @param {string} pieceName - Name of the piece (e.g., 'gmail', 'slack')
   * @returns {Promise<Object|null>} Piece details including actions and triggers
   */
  async getPieceDetails(pieceName) {
    const piece = await this.db.get(`
      SELECT * FROM pieces WHERE name = ?
    `, [pieceName]);

    if (!piece) {
      return null;
    }

    // Parse JSON fields
    if (piece.categories) {
      piece.categories = JSON.parse(piece.categories);
    }
    if (piece.authors) {
      piece.authors = JSON.parse(piece.authors);
    }

    // Get actions
    piece.actions = await this.db.all(`
      SELECT name, display_name, description, requires_auth
      FROM actions
      WHERE piece_id = ?
    `, [piece.id]);

    // Get triggers
    piece.triggers = await this.db.all(`
      SELECT name, display_name, description, trigger_type, requires_auth
      FROM triggers
      WHERE piece_id = ?
    `, [piece.id]);

    return piece;
  }

  /**
   * Get input properties for a specific action
   * @param {string} pieceName - Name of the piece (e.g., 'gmail')
   * @param {string} actionName - Name of the action (e.g., 'send_email')
   * @returns {Promise<Array>} List of input properties
   */
  async getActionInputs(pieceName, actionName) {
    return await this.db.all(`
      SELECT 
        ap.name,
        ap.display_name,
        ap.description,
        ap.type,
        ap.required,
        ap.default_value
      FROM pieces p
      JOIN actions a ON p.id = a.piece_id
      JOIN action_properties ap ON a.id = ap.action_id
      WHERE p.name = ? AND a.name = ?
      ORDER BY ap.required DESC, ap.display_name
    `, [pieceName, actionName]);
  }

  /**
   * Get the most capable pieces (by action + trigger count)
   * @param {number} limit - Maximum number of pieces to return
   * @returns {Promise<Array>} List of pieces ordered by capabilities
   */
  async getTopPieces(limit = 20) {
    return await this.db.all(`
      SELECT 
        display_name,
        auth_type,
        action_count,
        trigger_count,
        (action_count + trigger_count) as total_capabilities
      FROM pieces_with_capabilities
      WHERE action_count > 0 OR trigger_count > 0
      ORDER BY total_capabilities DESC
      LIMIT ?
    `, [limit]);
  }

  /**
   * Get all pieces with their action and trigger counts
   * @returns {Promise<Array>} List of all pieces
   */
  async getAllPieces() {
    return await this.db.all(`
      SELECT 
        name,
        display_name,
        auth_type,
        action_count,
        trigger_count
      FROM pieces_with_capabilities
      ORDER BY display_name
    `);
  }

  /**
   * Get pieces by authentication type
   * @param {string} authType - Authentication type (e.g., 'OAuth2', 'ApiKey')
   * @returns {Promise<Array>} List of pieces with that auth type
   */
  async getPiecesByAuthType(authType) {
    return await this.db.all(`
      SELECT display_name, action_count, trigger_count
      FROM pieces_with_capabilities
      WHERE auth_type = ?
      ORDER BY (action_count + trigger_count) DESC
    `, [authType]);
  }
}

async function main() {
  console.log('🤖 Activepieces Database - Node.js Example\n');

  const db = new ActivepiecesDB();
  await db.connect();

  try {
    // Example 1: Search for pieces related to email
    console.log('📧 Example 1: Search for email-related pieces');
    console.log('-'.repeat(50));
    const emailPieces = await db.searchPieces('email', 5);
    for (const piece of emailPieces) {
      console.log(`  • ${piece.display_name}`);
      console.log(`    ${piece.action_count} actions, ${piece.trigger_count} triggers`);
    }
    console.log();

    // Example 2: Search for "send email" actions
    console.log('✉️ Example 2: Find "send email" actions');
    console.log('-'.repeat(50));
    const sendActions = await db.searchActions('send email', 5);
    for (const action of sendActions) {
      console.log(`  • ${action.piece_display_name}: ${action.action_display_name}`);
    }
    console.log();

    // Example 3: Get Gmail piece details
    console.log('📬 Example 3: Gmail piece details');
    console.log('-'.repeat(50));
    const gmail = await db.getPieceDetails('gmail');
    if (gmail) {
      console.log(`  Name: ${gmail.display_name}`);
      console.log(`  Auth Type: ${gmail.auth_type}`);
      console.log(`  Actions: ${gmail.actions.length}`);
      console.log(`  Triggers: ${gmail.triggers.length}`);
    }
    console.log();

    // Example 4: Get inputs for Gmail Send Email action
    console.log('📝 Example 4: Gmail Send Email inputs');
    console.log('-'.repeat(50));
    const inputs = await db.getActionInputs('gmail', 'send_email');
    for (const input of inputs.slice(0, 5)) {  // Show first 5
      const required = input.required ? '✓' : ' ';
      console.log(`  [${required}] ${input.display_name} (${input.type})`);
    }
    console.log();

    console.log('✅ All examples completed successfully!');

  } finally {
    await db.close();
  }
}

// Run examples if this file is executed directly
if (require.main === module) {
  main().catch(error => {
    console.error('Error:', error);
    process.exit(1);
  });
}

// Export the class for use in other modules
module.exports = ActivepiecesDB;

