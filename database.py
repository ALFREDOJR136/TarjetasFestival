"""
Esquema de base de datos y modelos de datos para el Sistema de Pago con Tarjetas de Eventos.
Este módulo define todas las estructuras de datos necesarias para el sistema.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from dataclasses import dataclass, field


class CardStatus(Enum):
    """Enumeración de estados de tarjeta"""
    ACTIVE = "ACTIVE"
    BLOCKED = "BLOCKED"


class TransactionType(Enum):
    """Enumeración de tipos de transacción"""
    PAYMENT = "PAYMENT"
    RECHARGE = "RECHARGE"


class OperationType(Enum):
    """Tipo de operación para registro de auditoría"""
    CARD_ISSUED = "CARD_ISSUED"
    CARD_ACTIVATED = "CARD_ACTIVATED"
    CARD_BLOCKED = "CARD_BLOCKED"
    CARD_RECHARGED = "CARD_RECHARGED"
    PAYMENT_MADE = "PAYMENT_MADE"
    BALANCE_QUERY = "BALANCE_QUERY"
    HISTORY_QUERY = "HISTORY_QUERY"


@dataclass
class User:
    """Entidad de Usuario"""
    user_id: str
    name: str
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Card:
    """Entidad de Tarjeta de Evento"""
    card_id: str
    user_id: str
    balance: float
    status: CardStatus
    issued_at: datetime = field(default_factory=datetime.now)
    activated_at: Optional[datetime] = None
    blocked_at: Optional[datetime] = None


@dataclass
class Transaction:
    """Registro de transacción (pagos y recargas)"""
    transaction_id: str
    card_id: str
    transaction_type: TransactionType
    amount: float
    timestamp: datetime = field(default_factory=datetime.now)
    terminal_id: Optional[str] = None  # Para pagos
    organizer_id: Optional[str] = None  # Para recargas
    description: str = ""


@dataclass
class AuditLog:
    """Entrada de registro de auditoría para todas las operaciones del sistema"""
    log_id: str
    operation_type: OperationType
    timestamp: datetime
    actor_id: str  # Quién realizó la operación
    card_id: Optional[str] = None
    details: str = ""


class Database:
    """Base de datos en memoria para el sistema de tarjetas de eventos"""
    
    def __init__(self):
        self.users: Dict[str, User] = {}
        self.cards: Dict[str, Card] = {}
        self.transactions: List[Transaction] = []
        self.audit_logs: List[AuditLog] = []
        
        # Contadores para generar IDs
        self._transaction_counter = 0
        self._audit_log_counter = 0
    
    def add_user(self, user: User) -> None:
        """Añadir un usuario a la base de datos"""
        self.users[user.user_id] = user
    
    def get_user(self, user_id: str) -> Optional[User]:
        """Obtener un usuario por ID"""
        return self.users.get(user_id)
    
    def add_card(self, card: Card) -> None:
        """Añadir una tarjeta a la base de datos"""
        self.cards[card.card_id] = card
    
    def get_card(self, card_id: str) -> Optional[Card]:
        """Obtener una tarjeta por ID"""
        return self.cards.get(card_id)
    
    def update_card(self, card: Card) -> None:
        """Actualizar una tarjeta en la base de datos"""
        self.cards[card.card_id] = card
    
    def add_transaction(self, transaction: Transaction) -> None:
        """Añadir una transacción a la base de datos"""
        self.transactions.append(transaction)
    
    def get_card_transactions(self, card_id: str) -> List[Transaction]:
        """Obtener todas las transacciones de una tarjeta específica"""
        return [t for t in self.transactions if t.card_id == card_id]
    
    def add_audit_log(self, log: AuditLog) -> None:
        """Añadir una entrada de registro de auditoría"""
        self.audit_logs.append(log)
    
    def generate_transaction_id(self) -> str:
        """Generar un ID de transacción único"""
        self._transaction_counter += 1
        return f"TXN{self._transaction_counter:08d}"
    
    def generate_audit_log_id(self) -> str:
        """Generar un ID de registro de auditoría único"""
        self._audit_log_counter += 1
        return f"LOG{self._audit_log_counter:08d}"


# Instancia global de base de datos
db = Database()
