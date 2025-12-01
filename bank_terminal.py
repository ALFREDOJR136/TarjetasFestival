"""
API de Terminal Bancario - maneja consultas de saldo y visualización de historial de transacciones.
Los usuarios SOLO pueden consultar saldo y ver historial. No se permiten otras operaciones.
"""

from datetime import datetime
from typing import Dict, Any, List

from database import db, AuditLog, OperationType
from errors import CardNotRegisteredError


class BankTerminal:
    """
    Terminal Bancario - permite a los usuarios ver saldo e historial de transacciones.
    NO se permiten depósitos, retiros, transferencias o cambios de cuenta.
    """
    
    def __init__(self, terminal_id: str):
        self.terminal_id = terminal_id
    
    def check_balance(self, card_id: str) -> Dict[str, Any]:
        """
        Mostrar el saldo actual de una tarjeta.
        
        Args:
            card_id: Identificador de tarjeta
            
        Returns:
            Diccionario con el saldo y estado de la tarjeta
            
        Raises:
            CardNotRegisteredError: Si la tarjeta no existe
        """
        card = db.get_card(card_id)
        if not card:
            raise CardNotRegisteredError(card_id)
        
        # Registrar la consulta de saldo
        log = AuditLog(
            log_id=db.generate_audit_log_id(),
            operation_type=OperationType.BALANCE_QUERY,
            timestamp=datetime.now(),
            actor_id=self.terminal_id,
            card_id=card_id,
            details=f"Saldo consultado en el terminal {self.terminal_id}"
        )
        db.add_audit_log(log)
        
        return {
            "card_id": card.card_id,
            "balance": card.balance,
            "status": card.status.value,
            "user_id": card.user_id,
            "queried_at": datetime.now().isoformat()
        }
    
    def view_transaction_history(self, card_id: str) -> Dict[str, Any]:
        """
        Mostrar el historial completo de transacciones (pagos y recargas).
        
        Args:
            card_id: Identificador de tarjeta
            
        Returns:
            Diccionario con la información de la tarjeta y lista de todas las transacciones
            
        Raises:
            CardNotRegisteredError: Si la tarjeta no existe
        """
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
        
        # Registrar la consulta de historial
        log = AuditLog(
            log_id=db.generate_audit_log_id(),
            operation_type=OperationType.HISTORY_QUERY,
            timestamp=datetime.now(),
            actor_id=self.terminal_id,
            card_id=card_id,
            details=f"Historial de transacciones consultado en el terminal {self.terminal_id}"
        )
        db.add_audit_log(log)
        
        return {
            "card_id": card.card_id,
            "user_id": card.user_id,
            "current_balance": card.balance,
            "status": card.status.value,
            "transaction_count": len(transaction_list),
            "transactions": sorted(
                transaction_list,
                key=lambda x: x["timestamp"],
                reverse=True  # Más recientes primero
            ),
            "queried_at": datetime.now().isoformat()
        }
    
    def list_valid_event_cards(self) -> List[Dict[str, Any]]:
        """
        Listar todas las tarjetas de evento válidas registradas en el sistema.
        
        Returns:
            Lista de información de tarjetas
        """
        cards = []
        for card in db.cards.values():
            cards.append({
                "card_id": card.card_id,
                "user_id": card.user_id,
                "status": card.status.value,
                "balance": card.balance
            })
        
        return sorted(cards, key=lambda x: x["card_id"])
    
    def list_recharges(self, card_id: str = None) -> List[Dict[str, Any]]:
        """
        Listar todas las recargas realizadas por el organizador.
        
        Args:
            card_id: ID de tarjeta opcional para filtrar recargas
            
        Returns:
            Lista de transacciones de recarga
        """
        from database import TransactionType
        
        recharges = [
            txn for txn in db.transactions
            if txn.transaction_type == TransactionType.RECHARGE
        ]
        
        # Filtrar por card_id si se proporciona
        if card_id:
            recharges = [txn for txn in recharges if txn.card_id == card_id]
        
        recharge_list = []
        for txn in recharges:
            recharge_list.append({
                "transaction_id": txn.transaction_id,
                "card_id": txn.card_id,
                "amount": txn.amount,
                "timestamp": txn.timestamp.isoformat(),
                "organizer_id": txn.organizer_id
            })
        
        return sorted(recharge_list, key=lambda x: x["timestamp"], reverse=True)
