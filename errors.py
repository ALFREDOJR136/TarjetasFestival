"""
Clases de errores para el Sistema de Pago con Tarjetas de Eventos.
Todas las excepciones personalizadas con mensajes de error específicos.
"""


class EventCardError(Exception):
    """Excepción base para todos los errores de tarjetas de eventos"""
    pass


class CardNotRegisteredError(EventCardError):
    """La tarjeta no está registrada para este evento"""
    def __init__(self, card_id: str):
        super().__init__(f"ERROR: Tarjeta {card_id} no registrada para este evento")
        self.card_id = card_id


class CardBlockedError(EventCardError):
    """La tarjeta está bloqueada y no puede ser usada"""
    def __init__(self, card_id: str):
        super().__init__(f"ERROR: Tarjeta {card_id} bloqueada")
        self.card_id = card_id


class InsufficientBalanceError(EventCardError):
    """La tarjeta tiene saldo insuficiente para la transacción"""
    def __init__(self, card_id: str, balance: float, amount: float):
        super().__init__(
            f"ERROR: Saldo insuficiente. La tarjeta {card_id} tiene ${balance:.2f}, "
            f"pero se requieren ${amount:.2f}"
        )
        self.card_id = card_id
        self.balance = balance
        self.amount = amount


class InvalidCardError(EventCardError):
    """El ID de tarjeta es inválido"""
    def __init__(self, card_id: str):
        super().__init__(f"ERROR: Tarjeta inválida {card_id}")
        self.card_id = card_id


class ConnectionFailureError(EventCardError):
    """La conexión al sistema ha fallado"""
    def __init__(self):
        super().__init__("ERROR: Fallo de conexión")


class OperationNotPermittedError(EventCardError):
    """La operación no está permitida"""
    def __init__(self, operation: str, actor: str):
        super().__init__(f"ERROR: Operación no permitida - {actor} no puede {operation}")
        self.operation = operation
        self.actor = actor


class UserNotFoundError(EventCardError):
    """El usuario no existe"""
    def __init__(self, user_id: str):
        super().__init__(f"ERROR: Usuario {user_id} no encontrado")
        self.user_id = user_id


class CardAlreadyExistsError(EventCardError):
    """El ID de tarjeta ya existe en el sistema"""
    def __init__(self, card_id: str):
        super().__init__(f"ERROR: La tarjeta {card_id} ya existe")
        self.card_id = card_id


class InvalidAmountError(EventCardError):
    """El monto es inválido (negativo o cero)"""
    def __init__(self, amount: float):
        super().__init__(f"ERROR: Monto inválido ${amount:.2f}")
        self.amount = amount
