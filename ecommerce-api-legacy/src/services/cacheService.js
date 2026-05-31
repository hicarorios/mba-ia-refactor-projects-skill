'use strict';
const { logger } = require('../utils/logger');

// Encapsulated cache with instance state — replaces the module-level
// mutable `globalCache` global.
class CacheService {
  constructor() {
    this.store = {};
  }

  set(key, value) {
    logger.info('cache.set', { key });
    this.store[key] = value;
  }

  get(key) {
    return this.store[key];
  }
}

module.exports = { CacheService };
