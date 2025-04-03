from aiogram.dispatcher.filters.state import State, StatesGroup

class UserStates(StatesGroup):
    get_promo_state = State()