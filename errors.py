"""
Clases de errores para el Sistema de Pago con Tarjetas de Eventos.
Todas las excepciones personalizadas con mensajes de error específicos.
"""


"""Excepción base para todos los errores de tarjetas de eventos"""
class EventCardError(Exception):
    pass


"""La tarjeta no está registrada para este evento"""
class CardNotRegisteredError(EventCardError):
    def __init__(self, card_id: str):
        super().__init__(f"ERROR: Tarjeta {card_id} no registrada para este evento")
        self.card_id = card_id


"""La tarjeta tiene saldo insuficiente para la transacción"""
class InsufficientBalanceError(EventCardError):
    def __init__(self, card_id: str, balance: float, amount: float):
        super().__init__(
            f"ERROR: Saldo insuficiente. La tarjeta {card_id} tiene ${balance:.2f}, "
            f"pero se requieren ${amount:.2f}"
        )
        self.card_id = card_id
        self.balance = balance
        self.amount = amount


"""La conexión al sistema ha fallado"""
class ConnectionFailureError(EventCardError):
    def __init__(self):
        super().__init__("ERROR: Fallo de conexión")


"""El usuario no existe"""
class UserNotFoundError(EventCardError):
    def __init__(self, user_id: str):
        super().__init__(f"ERROR: Usuario {user_id} no encontrado")
        self.user_id = user_id


"""El ID de tarjeta ya existe en el sistema"""
class CardAlreadyExistsError(EventCardError):
    def __init__(self, card_id: str):
        super().__init__(f"ERROR: La tarjeta {card_id} ya existe")
        self.card_id = card_id


"""El monto es inválido (negativo o cero)"""
class InvalidAmountError(EventCardError):
    def __init__(self, amount: float):
        super().__init__(f"ERROR: Monto inválido ${amount:.2f}")
        self.amount = amount
