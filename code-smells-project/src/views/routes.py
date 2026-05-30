"""Routing only — maps method+path to controller actions. No business logic."""
from flask import jsonify


def register_routes(app, c):
    """`c` is a namespace of controller instances wired in the composition root."""

    @app.route("/")
    def index():
        return jsonify({
            "mensagem": "Bem-vindo à API da Loja",
            "versao": "1.0.0",
            "endpoints": {
                "produtos": "/produtos",
                "usuarios": "/usuarios",
                "pedidos": "/pedidos",
                "login": "/login",
                "relatorios": "/relatorios/vendas",
                "health": "/health",
            },
        })

    # Produtos
    app.add_url_rule("/produtos", "listar_produtos", c.produto.listar, methods=["GET"])
    app.add_url_rule("/produtos/busca", "buscar_produtos", c.produto.buscar_lista, methods=["GET"])
    app.add_url_rule("/produtos/<int:id>", "buscar_produto", c.produto.buscar, methods=["GET"])
    app.add_url_rule("/produtos", "criar_produto", c.produto.criar, methods=["POST"])
    app.add_url_rule("/produtos/<int:id>", "atualizar_produto", c.produto.atualizar, methods=["PUT"])
    app.add_url_rule("/produtos/<int:id>", "deletar_produto", c.produto.deletar, methods=["DELETE"])

    # Usuários
    app.add_url_rule("/usuarios", "listar_usuarios", c.usuario.listar, methods=["GET"])
    app.add_url_rule("/usuarios/<int:id>", "buscar_usuario", c.usuario.buscar, methods=["GET"])
    app.add_url_rule("/usuarios", "criar_usuario", c.usuario.criar, methods=["POST"])
    app.add_url_rule("/login", "login", c.usuario.login, methods=["POST"])

    # Pedidos
    app.add_url_rule("/pedidos", "criar_pedido", c.pedido.criar, methods=["POST"])
    app.add_url_rule("/pedidos", "listar_todos_pedidos", c.pedido.listar_todos, methods=["GET"])
    app.add_url_rule("/pedidos/usuario/<int:usuario_id>", "listar_pedidos_usuario", c.pedido.listar_por_usuario, methods=["GET"])
    app.add_url_rule("/pedidos/<int:pedido_id>/status", "atualizar_status_pedido", c.pedido.atualizar_status, methods=["PUT"])

    # Relatórios
    app.add_url_rule("/relatorios/vendas", "relatorio_vendas", c.relatorio.vendas, methods=["GET"])

    # Health
    app.add_url_rule("/health", "health_check", c.health.check, methods=["GET"])

    # Admin (kept for contract compatibility, capabilities neutralized)
    app.add_url_rule("/admin/query", "executar_query", c.admin.executar_query, methods=["POST"])
    app.add_url_rule("/admin/reset-db", "reset_database", c.admin.reset_db, methods=["POST"])
