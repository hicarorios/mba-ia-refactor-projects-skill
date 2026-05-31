'use strict';

class CheckoutController {
  constructor(checkoutService) {
    this.checkoutService = checkoutService;
  }

  // Thin: maps the request body to the service call. No business logic.
  async checkout(req, res) {
    const result = await this.checkoutService.checkout({
      name: req.body.usr,
      email: req.body.eml,
      password: req.body.pwd,
      courseId: req.body.c_id,
      card: req.body.card,
    });
    res.status(200).json(result);
  }
}

module.exports = { CheckoutController };
