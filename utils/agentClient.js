// utils/agentClient.js
// Central client for invoking agents via a unified message queue.
// Writes a message to shared/event_log.jsonl and waits for a response.

import fs from 'fs';
import path from 'path';
import { v4 as uuidv4 } from 'uuid';

const EVENT_LOG_PATH = path.resolve(process.cwd(), 'shared', 'event_log.jsonl');
const RESPONSE_TIMEOUT_MS = 30000; // 30 seconds max wait

/**
 * Write a message to the event log.
 * @param {Object} msg - Message object to serialize.
 */
function writeToQueue(msg) {
  const line = JSON.stringify(msg) + '\n';
  fs.appendFileSync(EVENT_LOG_PATH, line, { encoding: 'utf8' });
}

/**
 * Wait for a response with matching id.
 * Polls the event log for a line where status === 'done' and id matches.
 * @param {string} id - UUID of the original message.
 * @returns {Promise<any>} Resolved with response payload.
 */
function waitForResponse(id) {
  return new Promise((resolve, reject) => {
    const start = Date.now();
    const interval = setInterval(() => {
      if (Date.now() - start > RESPONSE_TIMEOUT_MS) {
        clearInterval(interval);
        reject(new Error('Response timeout for message id ' + id));
        return;
      }
      const content = fs.readFileSync(EVENT_LOG_PATH, 'utf8');
      const lines = content.trim().split('\n');
      for (const line of lines) {
        try {
          const obj = JSON.parse(line);
          if (obj.id === id && obj.status === 'done') {
            clearInterval(interval);
            resolve(obj.response);
            return;
          }
        } catch (e) {
          // ignore malformed lines
        }
      }
    }, 500);
  });
}

/**
 * Main exported function to call an agent.
 * @param {string} agentId - Target agent identifier.
 * @param {string} action - Action name.
 * @param {Object} payload - Payload for the action.
 * @returns {Promise<any>} Agent response.
 */
export async function callAgent(agentId, action, payload) {
  const msg = {
    id: uuidv4(),
    ts: Date.now(),
    agentId,
    action,
    payload,
    status: 'pending'
  };
  writeToQueue(msg);
  // In real system another process will pick up the message and update status.
  return await waitForResponse(msg.id);
}

// Export for convenience when using CommonJS
export default { callAgent };
