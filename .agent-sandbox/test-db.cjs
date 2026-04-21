const Database = require('better-sqlite3');
const path = require('path');
const dbPath = '/Users/igorvasin/freelance-2026/freelance-agent/data/db/freelance.db';
try {
  const db = new Database(dbPath, { readonly: true });
  const row = db.prepare('SELECT count(*) as count FROM jobs').get();
  console.log('Count:', row.count);
  db.close();
} catch (err) {
  console.error('Error:', err.message);
}
