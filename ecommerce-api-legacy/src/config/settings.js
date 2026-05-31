'use strict';
// Configuration sourced from environment variables. No secret is hardcoded.
// Copy .env.example to .env to run locally.
require('dotenv').config();

function required(key) {
  const value = process.env[key];
  if (!value) {
    throw new Error(`${key} is required — copy .env.example to .env and fill it in`);
  }
  return value;
}

const settings = {
  port: parseInt(process.env.PORT || '3000', 10),
  env: process.env.APP_ENV || 'development',
  paymentGatewayKey: required('PAYMENT_GATEWAY_KEY'),
  smtpUser: process.env.SMTP_USER || '',
};

module.exports = { settings };
