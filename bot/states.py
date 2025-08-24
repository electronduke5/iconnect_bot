from aiogram.fsm.state import State, StatesGroup

class CategoryCreation(StatesGroup):
    """
    Состояния для создания категории
    """
    waiting_for_name = State()