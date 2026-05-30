"""Domain constants — replaces magic numbers scattered through the code."""

# Sales report discount tiers: (minimum gross revenue, discount rate).
# Evaluated top-down; the first matching tier applies.
DISCOUNT_TIERS = [
    (10_000, 0.10),
    (5_000, 0.05),
    (1_000, 0.02),
]

VALID_PRODUCT_CATEGORIES = [
    "informatica", "moveis", "vestuario", "geral", "eletronicos", "livros",
]

VALID_ORDER_STATUSES = [
    "pendente", "aprovado", "enviado", "entregue", "cancelado",
]

PRODUCT_NAME_MIN_LEN = 2
PRODUCT_NAME_MAX_LEN = 200
