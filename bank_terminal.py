"""
API de Terminal Bancario - maneja consultas de saldo y visualización de historial de transacciones.
Los usuarios SOLO pueden consultar saldo y ver historial. No se permiten otras operaciones.
"""

from datetime import datetime
from typing import Dict, Any, List

from database import db
from errors import CardNotRegisteredError


"""Terminal Bancario"""
class BankTerminal:
    
    def __init__(self, terminal_id: str):
        self.terminal_id = terminal_id
    
    """Mostrar el saldo actual de una tarjeta."""
    def check_balance(self, card_id: str) -> Dict[str, Any]:
        
        card = db.get_card(card_id)
        if not card:
            raise CardNotRegisteredError(card_id)
        
        return {
            "card_id": card.card_id,
            "balance": card.balance,
            "user_id": card.user_id,
            "queried_at": datetime.now().isoformat()
        }
    
    """Mostrar el historial completo de transacciones (pagos y recargas)."""
    def view_transaction_history(self, card_id: str) -> Dict[str, Any]:

        card = db.get_card(card_id)
        if not card:
            raise CardNotRegisteredError(card_id)
        
        # Obtener todas las transacciones de esta tarjeta
        transactions = db.get_card_transactions(card_id)
        
        # Formatear transacciones
        transaction_list = []
        for txn in transactions:
            txn_data = {
                "transaction_id": txn.transaction_id,
                "type": txn.transaction_type.value,
                "amount": txn.amount,
                "timestamp": txn.timestamp.isoformat(),
                "description": txn.description
            }
            
            # Añadir ID de terminal para pagos
            if txn.terminal_id:
                txn_data["terminal_id"] = txn.terminal_id
            
            # Añadir ID de organizador para recargas
            if txn.organizer_id:
                txn_data["organizer_id"] = txn.organizer_id
            
            transaction_list.append(txn_data)
        
        return {
            "card_id": card.card_id,
            "user_id": card.user_id,
            "current_balance": card.balance,
            "transaction_count": len(transaction_list),
            "transactions": sorted(
                transaction_list,
                key=lambda x: x["timestamp"],
                reverse=True  # Más recientes primero
            ),
            "queried_at": datetime.now().isoformat()
        }
