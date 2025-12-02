# Sistema de Pago con Tarjetas para Eventos

Sistema de pago con tarjetas prepagadas para festivales y eventos. Permite gestionar tarjetas específicas del evento que los usuarios utilizan para realizar compras en las tiendas y stands.

## 🎯 ¿De qué trata el proyecto?

Este sistema está diseñado para eventos cerrados donde:
- Los usuarios reciben tarjetas prepagadas para usar exclusivamente dentro del evento
- Solo se aceptan tarjetas físicas del evento (no apps móviles/NFC)
- Las tarjetas son no reembolsables y expiran al final del evento
- Solo el organizador del evento puede gestionar tarjetas y recargas
- La seguridad se aplica mediante bloqueo de tarjetas (no requiere PIN)

## 👥 Actores del Sistema

### Organizador del Evento
- ✅ Emitir nuevas tarjetas
- ✅ Recargar tarjetas (añadir fondos)

### Terminales Bancarios
- ✅ Mostrar saldo actual de la tarjeta
- ✅ Mostrar historial completo de transacciones

### Usuarios
- ✅ Recibir tarjetas del organizador
- ✅ Pagar en tiendas/stands del evento
- ✅ Consultar saldo e historial en terminales bancarios

**No pueden:**
- ❌ Recargar sus propias tarjetas
- ❌ Realizar operaciones financieras excepto pagos

## 🚀 Cómo ejecutar la demo

```bash
python demo.py
```

Esto ejecutará 3 escenarios de demostración:
1. **Ciclo de vida normal de la tarjeta** - Crear usuario, emitir tarjeta, recargar, pagar
2. **Saldo insuficiente** - Intentar pagar más del saldo disponible
3. **Tarjeta inválida** - Intentar usar una tarjeta no registrada

## 📁 Archivos del Proyecto

- **`database.py`** - Modelos de datos y base de datos en memoria
- **`errors.py`** - Excepciones personalizadas del sistema
- **`organizer.py`** - API del Organizador del Evento
- **`bank_terminal.py`** - API de Terminales Bancarios
- **`payment_terminal.py`** - API de Terminales de Pago
- **`demo.py`** - Demostración interactiva del sistema

## 🔒 Reglas de Seguridad

1. **No se requiere PIN** - Si roban una tarjeta, se pierden los fondos
2. **No reembolsable** - Todo el dinero añadido a las tarjetas es permanente
3. **Solo para el evento** - Las tarjetas expiran al final del evento; el saldo restante se pierde
4. **Operaciones solo del organizador** - Solo el organizador puede emitir y recargar tarjetas
5. **Fallos de conexión** - Los pagos se deniegan si el terminal pierde conexión

## 💡 Ejemplo de uso básico

```python
from organizer import EventOrganizer
from bank_terminal import BankTerminal
from payment_terminal import PaymentTerminal

# Inicializar componentes
organizer = EventOrganizer("ORG001")
bank = BankTerminal("BANK001")
shop = PaymentTerminal("SHOP001", "Tienda de Comida")

# Crear usuario y emitir tarjeta
organizer.create_user("USER001", "Juan Pérez")
card = organizer.issue_card("CARD001", "USER001", initial_balance=0.0)

# Recargar tarjeta
organizer.recharge_card("CARD001", 50.0)

# Realizar pago
payment = shop.process_payment("CARD001", 15.50)

# Consultar saldo
balance = bank.check_balance("CARD001")
print(f"Saldo actual: ${balance['balance']:.2f}")
```