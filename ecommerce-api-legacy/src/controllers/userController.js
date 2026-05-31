'use strict';

class UserController {
  constructor(userService) {
    this.userService = userService;
  }

  async delete(req, res) {
    await this.userService.deleteUser(req.params.id);
    res.send('Usuário deletado com sucesso (matrículas e pagamentos removidos em cascata).');
  }
}

module.exports = { UserController };
