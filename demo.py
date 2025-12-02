"""
Script de ejemplo/demo para el Sistema de Pago con Tarjetas de Eventos.
Demuestra toda la funcionalidad con escenarios realistas.
"""

from organizer import EventOrganizer
from bank_terminal import BankTerminal
from payment_terminal import PaymentTerminal
from errors import (
    InsufficientBalanceError,
    CardNotRegisteredError
)


def print_section(title: str):
    """Imprimir un encabezado de sección"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def main():
    """Ejecutar demostración completa del sistema de tarjetas de eventos"""
    
    print_section("SISTEMA DE PAGO CON TARJETAS DE EVENTOS - DEMO")
    
    # Inicializar actores
    organizer = EventOrganizer(organizer_id="ORG001")
    bank_terminal = BankTerminal(terminal_id="BANK001")
    food_terminal = PaymentTerminal(terminal_id="TERM001", shop_name="Puesto de Comida")
    merch_terminal = PaymentTerminal(terminal_id="TERM002", shop_name="Tienda de Merchandising")
    
    # ========================================
    # ESCENARIO 1: Ciclo de Vida Normal de Tarjeta
    # ========================================
    print_section("ESCENARIO 1: Ciclo de Vida Normal de Tarjeta")
    
    # Crear usuario
    print("1. Creando usuario...")
    user1 = organizer.create_user(user_id="USER001", name="Alfredo Martínez")
    print(f"   ✓ Usuario creado: {user1['name']} (ID: {user1['user_id']})")
    
    # Emitir tarjeta con saldo inicial
    print("\n2. Emitiendo tarjeta...")
    card1 = organizer.issue_card(card_id="CARD001", user_id="USER001", initial_balance=0.0)
    print(f"   ✓ ID de Tarjeta: {card1['card_id']}")
    print(f"   ✓ Saldo inicial: ${card1['balance']:.2f}")
    print(f"   ✓ ID de Usuario: {card1['user_id']}")
    
    # Recargar antes de hacer pagos
    print("\n4. El organizador recarga la tarjeta antes de usar...")
    recharge = organizer.recharge_card(card_id="CARD001", amount=50.0)
    print(f"   ✓ Recarga exitosa: ${recharge['amount']:.2f}")
    print(f"   ✓ Nuevo saldo: ${recharge['new_balance']:.2f}")
    
    # Verificar saldo después de la recarga
    print("\n5. Usuario verifica saldo después de la recarga...")
    balance_info = bank_terminal.check_balance("CARD001")
    print(f"   ✓ Saldo actual: ${balance_info['balance']:.2f}")
    
    # Hacer pago
    print("\n6. Usuario paga en el puesto de comida...")
    payment1 = food_terminal.process_payment(card_id="CARD001", amount=15.50)
    print(f"   ✓ Pago: ${payment1['amount']:.2f}")
    print(f"   ✓ ID de Transacción: {payment1['transaction_id']}")
    
    # Hacer otro pago
    print("\n7. Usuario paga en la tienda de merchandising...")
    payment2 = merch_terminal.process_payment(card_id="CARD001", amount=20.00)
    print(f"   ✓ Pago: ${payment2['amount']:.2f}")
    print(f"   ✓ ID de Transacción: {payment2['transaction_id']}")
    
    # Consultar historial de transacciones
    print("\n8. Usuario ve historial de transacciones en el banco...")
    history = bank_terminal.view_transaction_history("CARD001")
    print(f"   ✓ Total de transacciones: {history['transaction_count']}")
    print(f"   ✓ Saldo actual: ${history['current_balance']:.2f}")
    print(f"\n   Historial de Transacciones:")
    for txn in history['transactions']:
        # Formatear timestamp para mostrar solo HH:MM
        from datetime import datetime
        timestamp = datetime.fromisoformat(txn['timestamp'])
        time_str = timestamp.strftime("%H:%M")
        print(f"     - {txn['type']}: ${txn['amount']:.2f} a las {time_str}")
        if 'terminal_id' in txn:
            print(f"       Terminal: {txn['terminal_id']}")
    
    # ========================================
    # ESCENARIO 2: Saldo Insuficiente
    # ========================================
    print_section("ESCENARIO 2: Saldo Insuficiente")
    
    print("1. Usuario intenta pagar más que su saldo...")
    balance_info = bank_terminal.check_balance("CARD001")
    print(f"   Saldo actual: ${balance_info['balance']:.2f}")
    
    try:
        payment = food_terminal.process_payment(card_id="CARD001", amount=100.00)
    except InsufficientBalanceError as e:
        print(f"   ✗ {str(e)}")
        print("   ✓ ¡Pago denegado correctamente!")
    
    # ========================================
    # ESCENARIO 3: Tarjeta Inválida
    # ========================================
    print_section("ESCENARIO 3: Tarjeta Inválida")
    
    print("1. Alguien intenta usar una tarjeta no registrada para este evento...")
    try:
        payment = food_terminal.process_payment(card_id="FAKE999", amount=5.00)
    except CardNotRegisteredError as e:
        print(f"   ✗ {str(e)}")
        print("   ✓ ¡Pago denegado correctamente!")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    main()
