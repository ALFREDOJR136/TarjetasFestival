"""
API del Organizador de Eventos - maneja emisión, activación, bloqueo y recarga de tarjetas.
Solo el organizador del evento puede realizar estas operaciones.
"""

from datetime import datetime
from typing import Dict, Any

from database import db, Card, Transaction, AuditLog, CardStatus, TransactionType, OperationType, User
from errors import (
    CardNotRegisteredError,
    CardAlreadyExistsError,
    UserNotFoundError,
    InvalidAmountError
)


class EventOrganizer:
    """Organizador de Eventos - la única entidad que puede emitir, activar, bloquear y recargar tarjetas"""
    
    def __init__(self, organizer_id: str):
        self.organizer_id = organizer_id
    
    def create_user(self, user_id: str, name: str) -> Dict[str, Any]:
        """
        Crear un nuevo usuario en el sistema.
        
        Args:
            user_id: Identificador único de usuario
            name: Nombre del usuario
            
        Returns:
            Diccionario con los detalles del usuario
        """
        user = User(user_id=user_id, name=name)
        db.add_user(user)
        
        # Registrar la operación
        log = AuditLog(
            log_id=db.generate_audit_log_id(),
            operation_type=OperationType.CARD_ISSUED,
            timestamp=datetime.now(),
            actor_id=self.organizer_id,
            details=f"Usuario {user_id} creado: {name}"
        )
        db.add_audit_log(log)
        
        return {
            "user_id": user.user_id,
            "name": user.name,
            "created_at": user.created_at.isoformat()
        }
    
    def issue_card(self, card_id: str, user_id: str, initial_balance: float = 0.0) -> Dict[str, Any]:
        """
        Emitir una nueva tarjeta a un usuario. Las tarjetas se emiten ya activadas.
        
        Args:
            card_id: Identificador único de tarjeta
            user_id: ID de usuario para asociar con la tarjeta
            initial_balance: Saldo inicial (por defecto 0.0)
            
        Returns:
            Diccionario con los detalles de la tarjeta
            
        Raises:
            CardAlreadyExistsError: Si el ID de tarjeta ya existe
            UserNotFoundError: Si el usuario no existe
            InvalidAmountError: Si el saldo inicial es negativo
        """
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
        
        # Crear tarjeta (ya activada)
        card = Card(
            card_id=card_id,
            user_id=user_id,
            balance=initial_balance,
            status=CardStatus.ACTIVE,
            activated_at=datetime.now()
        )
        
        db.add_card(card)
        
        # Registrar la operación
        log = AuditLog(
            log_id=db.generate_audit_log_id(),
            operation_type=OperationType.CARD_ISSUED,
            timestamp=datetime.now(),
            actor_id=self.organizer_id,
            card_id=card_id,
            details=f"Tarjeta emitida al usuario {user_id} con saldo ${initial_balance:.2f}"
        )
        db.add_audit_log(log)
        
        return {
            "card_id": card.card_id,
            "user_id": card.user_id,
            "balance": card.balance,
            "status": card.status.value,
            "issued_at": card.issued_at.isoformat(),
            "activated_at": card.activated_at.isoformat()
        }
    
    def activate_card(self, card_id: str) -> Dict[str, Any]:
        """
        Activar una tarjeta bloqueada.
        
        Args:
            card_id: Identificador de tarjeta
            
        Returns:
            Diccionario con los detalles actualizados de la tarjeta
            
        Raises:
            CardNotRegisteredError: Si la tarjeta no existe
        """
        card = db.get_card(card_id)
        if not card:
            raise CardNotRegisteredError(card_id)
        
        card.status = CardStatus.ACTIVE
        card.activated_at = datetime.now()
        card.blocked_at = None
        db.update_card(card)
        
        # Registrar la operación
        log = AuditLog(
            log_id=db.generate_audit_log_id(),
            operation_type=OperationType.CARD_ACTIVATED,
            timestamp=datetime.now(),
            actor_id=self.organizer_id,
            card_id=card_id,
            details=f"Tarjeta {card_id} activada"
        )
        db.add_audit_log(log)
        
        return {
            "card_id": card.card_id,
            "status": card.status.value,
            "activated_at": card.activated_at.isoformat()
        }
    
    def block_card(self, card_id: str, reason: str = "Usuario reportó pérdida") -> Dict[str, Any]:
        """
        Bloquear una tarjeta (ej., si el usuario la reporta perdida).
        
        Args:
            card_id: Identificador de tarjeta
            reason: Razón del bloqueo
            
        Returns:
            Diccionario con los detalles actualizados de la tarjeta
            
        Raises:
            CardNotRegisteredError: Si la tarjeta no existe
        """
        card = db.get_card(card_id)
        if not card:
            raise CardNotRegisteredError(card_id)
        
        card.status = CardStatus.BLOCKED
        card.blocked_at = datetime.now()
        db.update_card(card)
        
        # Registrar la operación
        log = AuditLog(
            log_id=db.generate_audit_log_id(),
            operation_type=OperationType.CARD_BLOCKED,
            timestamp=datetime.now(),
            actor_id=self.organizer_id,
            card_id=card_id,
            details=f"Tarjeta {card_id} bloqueada: {reason}"
        )
        db.add_audit_log(log)
        
        return {
            "card_id": card.card_id,
            "status": card.status.value,
            "blocked_at": card.blocked_at.isoformat(),
            "reason": reason
        }
    
    def recharge_card(self, card_id: str, amount: float) -> Dict[str, Any]:
        """
        Recargar una tarjeta con el monto especificado.
        
        Args:
            card_id: Identificador de tarjeta
            amount: Monto a añadir a la tarjeta
            
        Returns:
            Diccionario con la transacción y el saldo actualizado
            
        Raises:
            CardNotRegisteredError: Si la tarjeta no existe
            InvalidAmountError: Si el monto es <= 0
        """
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
        
        # Registrar la operación
        log = AuditLog(
            log_id=db.generate_audit_log_id(),
            operation_type=OperationType.CARD_RECHARGED,
            timestamp=datetime.now(),
            actor_id=self.organizer_id,
            card_id=card_id,
            details=f"Tarjeta recargada con ${amount:.2f}, nuevo saldo: ${card.balance:.2f}"
        )
        db.add_audit_log(log)
        
        return {
            "transaction_id": transaction.transaction_id,
            "card_id": card.card_id,
            "amount": amount,
            "new_balance": card.balance,
            "timestamp": transaction.timestamp.isoformat()
        }
