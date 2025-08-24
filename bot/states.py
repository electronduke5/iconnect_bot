from aiogram.fsm.state import State, StatesGroup

class CategoryCreation(StatesGroup):
    """
    Состояния для создания категории
    """
    waiting_for_name = State()

class ProductCreation(StatesGroup):
    """
    Состояния для создания продукта
    """
    waiting_for_name = State()
    waiting_for_purchase_price = State()
    waiting_for_quantity = State()
    waiting_for_color = State()
    waiting_for_condition = State()
    waiting_for_category = State()