"""
Terminal de Pago - maneja pagos en tiendas/stands del evento.
Valida tarjetas, verifica saldo, deduce monto y registra transacciones.
"""

from datetime import datetime
from typing import Dict, Any

from database import db, Transaction, AuditLog, CardStatus, TransactionType, OperationType
from errors import (
    CardNotRegisteredError,
    CardBlockedError,
    InsufficientBalanceError,
    InvalidAmountError,
    ConnectionFailureError
)


class PaymentTerminal:
    """
    Terminal de Pago en tiendas del evento - maneja pagos con tarjeta.
    No se requiere PIN. Si la tarjeta es robada, los fondos se pierden.
    """
    
    def __init__(self, terminal_id: str, shop_name: str = ""):
        self.terminal_id = terminal_id
        self.shop_name = shop_name
        self.is_connected = True  # Simular estado de conexión
    
    def process_payment(self, card_id: str, amount: float) -> Dict[str, Any]:
        """
        Procesar una transacción de pago.
        
        Pasos de validación:
        1. Verificar conexión
        2. Verificar que la tarjeta existe (pertenece a este evento)
        3. Verificar que la tarjeta está activa (no bloqueada)
        4. Verificar saldo suficiente
        5. Deducir monto
        6. Registrar transacción
        
        Args:
            card_id: Identificador de tarjeta
            amount: Monto del pago
            
        Returns:
            Diccionario con los detalles de la transacción
            
        Raises:
            ConnectionFailureError: Si el terminal no está conectado
            InvalidAmountError: Si el monto es <= 0
            CardNotRegisteredError: Si la tarjeta no existe
            CardBlockedError: Si la tarjeta está bloqueada
            InsufficientBalanceError: Si la tarjeta tiene saldo insuficiente
        """
        # Paso 1: Verificar conexión
        if not self.is_connected:
            raise ConnectionFailureError()
        
        # Validar monto
        if amount <= 0:
            raise InvalidAmountError(amount)
        
        # Paso 2: Leer tarjeta y verificar que pertenece a este evento
        card = db.get_card(card_id)
        if not card:
            raise CardNotRegisteredError(card_id)
        
        # Paso 3: Verificar que la tarjeta está activa
        if card.status == CardStatus.BLOCKED:
            raise CardBlockedError(card_id)
        
        # Paso 4: Verificar saldo suficiente
        if card.balance < amount:
            raise InsufficientBalanceError(card_id, card.balance, amount)
        
        # Paso 5: Deducir monto
        card.balance -= amount
        db.update_card(card)
        
        # Paso 6: Registrar transacción
        transaction = Transaction(
            transaction_id=db.generate_transaction_id(),
            card_id=card_id,
            transaction_type=TransactionType.PAYMENT,
            amount=amount,
            terminal_id=self.terminal_id,
            description=f"Pago en {self.shop_name or self.terminal_id}"
        )
        db.add_transaction(transaction)
        
        # Registrar el pago
        log = AuditLog(
            log_id=db.generate_audit_log_id(),
            operation_type=OperationType.PAYMENT_MADE,
            timestamp=datetime.now(),
            actor_id=self.terminal_id,
            card_id=card_id,
            details=f"Pago de ${amount:.2f} en {self.shop_name or self.terminal_id}, saldo restante: ${card.balance:.2f}"
        )
        db.add_audit_log(log)
        
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
    
    def set_connection_status(self, is_connected: bool) -> None:
        """
        Simular estado de conexión para pruebas.
        
        Args:
            is_connected: True si está conectado, False en caso contrario
        """
        self.is_connected = is_connected
    
    def verify_card(self, card_id: str) -> Dict[str, Any]:
        """
        Verificar una tarjeta sin procesar pago (para pruebas/validación).
        
        Args:
            card_id: Identificador de tarjeta
            
        Returns:
            Diccionario con el estado de validación de la tarjeta
            
        Raises:
            CardNotRegisteredError: Si la tarjeta no existe
            CardBlockedError: Si la tarjeta está bloqueada
        """
        # Verificar conexión
        if not self.is_connected:
            raise ConnectionFailureError()
        
        # Verificar que la tarjeta existe
        card = db.get_card(card_id)
        if not card:
            raise CardNotRegisteredError(card_id)
        
        # Verificar que la tarjeta está activa
        if card.status == CardStatus.BLOCKED:
            raise CardBlockedError(card_id)
        
        return {
            "card_id": card.card_id,
            "user_id": card.user_id,
            "status": card.status.value,
            "balance": card.balance,
            "valid": True
        }
