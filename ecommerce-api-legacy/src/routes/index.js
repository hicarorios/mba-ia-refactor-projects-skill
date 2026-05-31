'use strict';
const express = require('express');
const { asyncHandler } = require('../middlewares/errorHandler');

// Routing only — maps method+path to controller actions.
function buildRouter(c) {
  const router = express.Router();

  router.post('/checkout', asyncHandler((req, res) => c.checkout.checkout(req, res)));
  router.get('/admin/financial-report', asyncHandler((req, res) => c.report.financialReport(req, res)));
  router.delete('/users/:id', asyncHandler((req, res) => c.user.delete(req, res)));

  return router;
}

module.exports = { buildRouter };
