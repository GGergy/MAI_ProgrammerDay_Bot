from aiogram.filters.callback_data import CallbackData

class ReceiveQuestion(CallbackData, prefix="receive_question"):
    ...


class CheckProfile(CallbackData, prefix="check_profile"):
    ...
    
    
class CheckLadder(CallbackData, prefix="check_ladder"):
    ...


class CheckPrizes(CallbackData, prefix="check_prizes"):
    ...