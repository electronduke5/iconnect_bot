from aiogram.fsm.state import State, StatesGroup

class CategoryCreation(StatesGroup):
    """
    Состояния для создания категории
    """
    waiting_for_name = State()

class SaleProcess(StatesGroup):
    """
    Состояния для процесса продажи товара/телефона
    """
    waiting_for_sale_price = State()

class ProductCreation(StatesGroup):
    """
    Состояния для создания продукта
    """
    waiting_for_name = State()
    waiting_for_category = State()
    waiting_for_purchase_price = State()
    waiting_for_quantity = State()
    waiting_for_color = State()
    waiting_for_condition = State()
    
    # Специальные состояния для телефонов (расширенная структура)
    waiting_for_brand = State()
    waiting_for_model = State() 
    waiting_for_storage_capacity = State()
    waiting_for_market = State()
    waiting_for_battery_health = State()
    waiting_for_repaired = State()
    waiting_for_full_kit = State()
    waiting_for_imei = State()
    waiting_for_serial_number = State()