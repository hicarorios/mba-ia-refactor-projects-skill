'use strict';
const { logger } = require('../utils/logger');

// Isolated payment "gateway". Card data is never logged in full; the gateway
// key is never logged.
class PaymentService {
  constructor(gatewayKey) {
    this.gatewayKey = gatewayKey;
  }

  charge(cardNumber, amount) {
    const masked = `****${String(cardNumber).slice(-4)}`;
    logger.info('payment.charge', { card: masked, amount });
    const status = String(cardNumber).startsWith('4') ? 'PAID' : 'DENIED';
    return { status };
  }
}

module.exports = { PaymentService };
