from aiogram import types, Router

from routers.shared.callbacks import DeleteCallback

router = Router(name=__name__)


@router.callback_query(DeleteCallback.filter())
async def close(query: types.CallbackQuery):
    await query.answer()
    if query.message.reply_to_message:
        await query.message.reply_to_message.delete()
    await query.message.delete()


@router.message()
async def deleter(message: types.Message):
    await message.delete()
