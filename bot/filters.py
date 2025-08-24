from aiogram import types
from aiogram.filters import BaseFilter

class IsAdminFilter(BaseFilter):
    admin_ids: list

    async def __call__(self, message: types.Message) -> bool:
        return message.from_user.id in self.admin_ids