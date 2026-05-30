"""Sales report computation — discount tiers come from named constants."""
from src.config.constants import DISCOUNT_TIERS


class RelatorioService:
    def __init__(self, pedido_model):
        self.pedido_model = pedido_model

    def vendas(self):
        row = self.pedido_model.report_counts()
        total_pedidos = row["total"] or 0
        faturamento = row["faturamento"] or 0

        desconto = 0
        for minimo, taxa in DISCOUNT_TIERS:
            if faturamento > minimo:
                desconto = faturamento * taxa
                break

        return {
            "total_pedidos": total_pedidos,
            "faturamento_bruto": round(faturamento, 2),
            "desconto_aplicavel": round(desconto, 2),
            "faturamento_liquido": round(faturamento - desconto, 2),
            "pedidos_pendentes": row["pendentes"] or 0,
            "pedidos_aprovados": row["aprovados"] or 0,
            "pedidos_cancelados": row["cancelados"] or 0,
            "ticket_medio": round(faturamento / total_pedidos, 2) if total_pedidos else 0,
        }
