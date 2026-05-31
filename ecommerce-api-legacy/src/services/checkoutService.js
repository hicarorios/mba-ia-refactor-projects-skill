'use strict';
const { AppError } = require('../middlewares/errorHandler');

// Orchestrates the checkout flow with async/await — replaces the deeply
// nested callback chain that lived inside the route handler.
class CheckoutService {
  constructor({ userRepo, courseRepo, enrollmentRepo, paymentRepo, auditRepo,
                paymentService, passwordService, cacheService }) {
    this.userRepo = userRepo;
    this.courseRepo = courseRepo;
    this.enrollmentRepo = enrollmentRepo;
    this.paymentRepo = paymentRepo;
    this.auditRepo = auditRepo;
    this.paymentService = paymentService;
    this.passwordService = passwordService;
    this.cacheService = cacheService;
  }

  async checkout({ name, email, password, courseId, card }) {
    if (!name || !email || !courseId || !card) {
      throw new AppError('Bad Request', 400);
    }

    const course = await this.courseRepo.findActiveById(courseId);
    if (!course) throw new AppError('Curso não encontrado', 404);

    let user = await this.userRepo.findByEmail(email);
    let userId;
    if (!user) {
      if (!password) throw new AppError('Senha é obrigatória para novo usuário', 400);
      const hash = this.passwordService.hash(password);
      userId = await this.userRepo.create(name, email, hash);
    } else {
      userId = user.id;
    }

    const { status } = this.paymentService.charge(card, course.price);
    if (status === 'DENIED') throw new AppError('Pagamento recusado', 400);

    const enrollmentId = await this.enrollmentRepo.create(userId, courseId);
    await this.paymentRepo.create(enrollmentId, course.price, status);
    await this.auditRepo.log(`Checkout curso ${courseId} por ${userId}`);
    this.cacheService.set(`last_checkout_${userId}`, course.title);

    return { msg: 'Sucesso', enrollment_id: enrollmentId };
  }
}

module.exports = { CheckoutService };
