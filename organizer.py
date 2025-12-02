"""
API del Organizador de Eventos - maneja emisión, activación, bloqueo y recarga de tarjetas.
Solo el organizador del evento puede realizar estas operaciones.
"""

from datetime import datetime
from typing import Dict, Any

from database import db, Card, Transaction, TransactionType, User
from errors import (
    CardNotRegisteredError,
    CardAlreadyExistsError,
    UserNotFoundError,
    InvalidAmountError
)


"""Organizador de Eventos."""
class EventOrganizer:
    
    def __init__(self, organizer_id: str):
        self.organizer_id = organizer_id

    """Crear un nuevo usuario en el sistema."""    
    def create_user(self, user_id: str, name: str) -> Dict[str, Any]:
        user = User(user_id=user_id, name=name)
        db.add_user(user)
        
        return {
            "user_id": user.user_id,
            "name": user.name
        }

    
    """Emitir una nueva tarjeta a un usuario."""
    def issue_card(self, card_id: str, user_id: str, initial_balance: float = 0.0) -> Dict[str, Any]:

        # Validar que el usuario existe
        user = db.get_user(user_id)
        if not user:
            raise UserNotFoundError(user_id)
        
        # Verificar si la tarjeta ya existe
        if db.get_card(card_id):
            raise CardAlreadyExistsError(card_id)
        
        # Validar saldo inicial
        if initial_balance < 0:
            raise InvalidAmountError(initial_balance)
        
        # Crear tarjeta
        card = Card(
            card_id=card_id,
            user_id=user_id,
            balance=initial_balance
        )
        
        db.add_card(card)
        
        return {
            "card_id": card.card_id,
            "user_id": card.user_id,
            "balance": card.balance
        }
    

    """Recargar una tarjeta con el monto especificado."""
    def recharge_card(self, card_id: str, amount: float) -> Dict[str, Any]:
        
        # Validar monto
        if amount <= 0:
            raise InvalidAmountError(amount)
        
        card = db.get_card(card_id)
        if not card:
            raise CardNotRegisteredError(card_id)
        
        # Actualizar saldo
        card.balance += amount
        db.update_card(card)
        
        # Registrar transacción
        transaction = Transaction(
            transaction_id=db.generate_transaction_id(),
            card_id=card_id,
            transaction_type=TransactionType.RECHARGE,
            amount=amount,
            organizer_id=self.organizer_id,
            description=f"Tarjeta recargada por el organizador"
        )
        db.add_transaction(transaction)
        
        return {
            "transaction_id": transaction.transaction_id,
            "card_id": card.card_id,
            "amount": amount,
            "new_balance": card.balance,
            "timestamp": transaction.timestamp.isoformat()
        }