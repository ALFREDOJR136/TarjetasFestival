"""
Terminal de Pago - maneja pagos en tiendas/stands del evento.
Valida tarjetas, verifica saldo, deduce monto y registra transacciones.
"""

from datetime import datetime
from typing import Dict, Any

from database import db, Transaction, TransactionType
from errors import (
    CardNotRegisteredError,
    InsufficientBalanceError,
    InvalidAmountError
)


"""Terminal de Pago en tiendas del evento."""
class PaymentTerminal:
    def __init__(self, terminal_id: str, shop_name: str = ""):
        self.terminal_id = terminal_id
        self.shop_name = shop_name
    
    """Procesar una transacción de pago."""
    def process_payment(self, card_id: str, amount: float) -> Dict[str, Any]:
        # Validar monto
        if amount <= 0:
            raise InvalidAmountError(amount)
        
        # Paso 1: Leer tarjeta y verificar que pertenece a este evento
        card = db.get_card(card_id)
        if not card:
            raise CardNotRegisteredError(card_id)
        
        # Paso 2: Verificar saldo suficiente
        if card.balance < amount:
            raise InsufficientBalanceError(card_id, card.balance, amount)
        
        # Paso 3: Deducir monto
        card.balance -= amount
        db.update_card(card)
        
        # Paso 4: Registrar transacción
        transaction = Transaction(
            transaction_id=db.generate_transaction_id(),
            card_id=card_id,
            transaction_type=TransactionType.PAYMENT,
            amount=amount,
            terminal_id=self.terminal_id,
            description=f"Pago en {self.shop_name or self.terminal_id}"
        )
        db.add_transaction(transaction)
        
        return {
            "transaction_id": transaction.transaction_id,
            "card_id": card.card_id,
            "amount": amount,
            "remaining_balance": card.balance,
            "terminal_id": self.terminal_id,
            "shop_name": self.shop_name,
            "timestamp": transaction.timestamp.isoformat(),
            "status": "SUCCESS"
        }