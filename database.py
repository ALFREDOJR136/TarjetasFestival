"""
Esquema de base de datos y modelos de datos para el Sistema de Pago con Tarjetas de Eventos.
Este módulo define todas las estructuras de datos necesarias para el sistema.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from dataclasses import dataclass, field


"""Tipos de transacción"""
class TransactionType(Enum):
    PAYMENT = "PAYMENT"
    RECHARGE = "RECHARGE"



"""Usuario"""
@dataclass
class User:
    user_id: str
    name: str



"""Tarjeta del Evento"""
@dataclass
class Card:
    card_id: str
    user_id: str
    balance: float



"""Registro de transacción (pagos y recargas)"""
@dataclass
class Transaction:
    transaction_id: str
    card_id: str
    transaction_type: TransactionType
    amount: float
    timestamp: datetime = field(default_factory=datetime.now)
    terminal_id: Optional[str] = None  # Para pagos
    organizer_id: Optional[str] = None  # Para recargas
    description: str = ""



"""Base de datos en memoria para el sistema de tarjetas de eventos"""
class Database:
    
    def __init__(self):
        self.users: Dict[str, User] = {}
        self.cards: Dict[str, Card] = {}
        self.transactions: List[Transaction] = []
        
        # Contador para generar IDs
        self._transaction_counter = 0
    
    """Añadir un usuario a la base de datos"""
    def add_user(self, user: User) -> None:
        self.users[user.user_id] = user

    """Obtener un usuario por ID"""    
    def get_user(self, user_id: str) -> Optional[User]:
        return self.users.get(user_id)
    
    """Añadir una tarjeta a la base de datos"""
    def add_card(self, card: Card) -> None:
        self.cards[card.card_id] = card
    
    """Obtener una tarjeta por ID"""
    def get_card(self, card_id: str) -> Optional[Card]:
        return self.cards.get(card_id)
    
    """Actualizar una tarjeta en la base de datos"""
    def update_card(self, card: Card) -> None:
        self.cards[card.card_id] = card

    """Añadir una transacción a la base de datos"""
    def add_transaction(self, transaction: Transaction) -> None:
        self.transactions.append(transaction)
    
    """Obtener todas las transacciones de una tarjeta específica"""
    def get_card_transactions(self, card_id: str) -> List[Transaction]:
        return [t for t in self.transactions if t.card_id == card_id]
    
    """Generar un ID de transacción único"""
    def generate_transaction_id(self) -> str:
        self._transaction_counter += 1
        return f"TXN{self._transaction_counter:08d}"


# Instancia global de base de datos
db = Database()
