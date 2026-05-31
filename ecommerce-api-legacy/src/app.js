'use strict';
// Composition root — builds the app, wires the layers, starts the server.
const express = require('express');

const { settings } = require('./config/settings');
const { logger } = require('./utils/logger');
const { Database } = require('./models/database');
const { UserRepository } = require('./models/userRepository');
const { CourseRepository } = require('./models/courseRepository');
const { EnrollmentRepository } = require('./models/enrollmentRepository');
const { PaymentRepository } = require('./models/paymentRepository');
const { AuditRepository } = require('./models/auditRepository');
const { ReportRepository } = require('./models/reportRepository');
const { CacheService } = require('./services/cacheService');
const { PaymentService } = require('./services/paymentService');
const { passwordService } = require('./services/passwordService');
const { CheckoutService } = require('./services/checkoutService');
const { ReportService } = require('./services/reportService');
const { UserService } = require('./services/userService');
const { CheckoutController } = require('./controllers/checkoutController');
const { ReportController } = require('./controllers/reportController');
const { UserController } = require('./controllers/userController');
const { buildRouter } = require('./routes');
const { errorHandler } = require('./middlewares/errorHandler');

function buildControllers(db) {
  const userRepo = new UserRepository(db);
  const courseRepo = new CourseRepository(db);
  const enrollmentRepo = new EnrollmentRepository(db);
  const paymentRepo = new PaymentRepository(db);
  const auditRepo = new AuditRepository(db);
  const reportRepo = new ReportRepository(db);

  const cacheService = new CacheService();
  const paymentService = new PaymentService(settings.paymentGatewayKey);

  const checkoutService = new CheckoutService({
    userRepo, courseRepo, enrollmentRepo, paymentRepo, auditRepo,
    paymentService, passwordService, cacheService,
  });
  const reportService = new ReportService(reportRepo);
  const userService = new UserService({ db, userRepo, enrollmentRepo, paymentRepo });

  return {
    checkout: new CheckoutController(checkoutService),
    report: new ReportController(reportService),
    user: new UserController(userService),
  };
}

function createApp(db) {
  const app = express();
  app.use(express.json());
  app.use('/api', buildRouter(buildControllers(db)));
  app.use(errorHandler);
  return app;
}

async function bootstrap() {
  const db = new Database(':memory:');
  await db.initialize();
  const app = createApp(db);
  app.listen(settings.port, () => {
    logger.info('server.started', { port: settings.port, env: settings.env });
  });
}

if (require.main === module) {
  bootstrap().catch((err) => {
    logger.error('bootstrap.failed', { error: err.message });
    process.exit(1);
  });
}

module.exports = { createApp, buildControllers };
