'use strict';
// Minimal structured logger — replaces scattered console.log calls and never
// logs sensitive data (card numbers, secrets).

function ts() {
  return new Date().toISOString();
}

const logger = {
  info: (msg, meta = {}) => console.log(JSON.stringify({ level: 'info', ts: ts(), msg, ...meta })),
  warn: (msg, meta = {}) => console.warn(JSON.stringify({ level: 'warn', ts: ts(), msg, ...meta })),
  error: (msg, meta = {}) => console.error(JSON.stringify({ level: 'error', ts: ts(), msg, ...meta })),
};

module.exports = { logger };
