/**
 * Example: How to use Activepieces database in Flow_Assistant project
 */

const ActivepiecesDB = require('./activepieces_db');

async function main() {
  console.log('=== Flow Assistant - Activepieces Integration ===\n');
  
  const db = new ActivepiecesDB();
  await db.connect();
  
  try {
    // Example 1: Search for pieces
    console.log('1. Search for email integrations:');
    const pieces = await db.searchPieces('email', 5);
    for (const piece of pieces) {
      console.log(`   • ${piece.display_name}: ${piece.action_count} actions`);
    }
    console.log();
    
    // Example 2: Find specific actions
    console.log('2. Find "send message" actions:');
    const actions = await db.searchActions('send message', 5);
    for (const action of actions) {
      console.log(`   • ${action.piece_display_name}: ${action.action_display_name}`);
    }
    console.log();
    
    // Example 3: Get action details
    console.log('3. Gmail Send Email - Required inputs:');
    const inputs = await db.getActionInputs('gmail', 'send_email');
    const requiredInputs = inputs.filter(inp => inp.required);
    for (const inp of requiredInputs) {
      console.log(`   • ${inp.display_name} (${inp.type})`);
    }
    console.log();
    
    // Example 4: Top integrations
    console.log('4. Top 10 integrations by capabilities:');
    const top = await db.getTopPieces(10);
    top.forEach((piece, i) => {
      const total = piece.action_count + piece.trigger_count;
      console.log(`   ${i + 1}. ${piece.display_name}: ${total} total capabilities`);
    });
    console.log();
    
    console.log('✅ Ready to use in Flow_Assistant!');
    
  } finally {
    await db.close();
  }
}

main().catch(console.error);


