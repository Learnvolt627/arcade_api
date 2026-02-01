class RFIDException(Exception):
    
    pass
class CardNotFoundError(RFIDException):
    def __init__(self, card_id: str):
        self.card_id =card_id


class CardAlreadyExistsError(RFIDException):
    def __init__(self, card_id: str):
        self.card_id =card_id


class BalanceLimitExceededError(RFIDException):
    def __init__(self, current_amount:float, attempted_amount: float, limit: float):
        self.current_amount = current_amount
        self.attempted_amount = attempted_amount
        self.limit = limit



