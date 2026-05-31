'use strict';
const { logger } = require('../utils/logger');

// Domain/HTTP error raised by services and controllers.
class AppError extends Error {
  constructor(message, status = 400) {
    super(message);
    this.status = status;
  }
}

// Wraps async route handlers so rejected promises reach the error handler
// instead of crashing or being swallowed.
const asyncHandler = (fn) => (req, res, next) =>
  Promise.resolve(fn(req, res, next)).catch(next);

// Centralized error handler — registered last. Replaces the inconsistent
// per-callback error handling of the original God Class.
function errorHandler(err, _req, res, _next) {
  if (err instanceof AppError) {
    return res.status(err.status).send(err.message);
  }
  logger.error('unhandled', { error: err.message });
  return res.status(500).send('Erro interno do servidor');
}

module.exports = { AppError, asyncHandler, errorHandler };
