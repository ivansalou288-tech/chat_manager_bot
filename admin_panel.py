from admin_config import *

@dp.callback_query_handler(text="admn_panell_check")
async def admn_panell_check(call: types.CallbackQuery):
    if call.from_user.id in can_admin_panel:
        await admin_panel(call)
        return
    else:
        await bot.answer_callback_query(call.id, text='Тебе не доступна эта функция', show_alert=True)
        return

@dp.callback_query_handler(text="admn_panel")
async def admin_panel(call: types.CallbackQuery):
    await bot.answer_callback_query(call.id, text='В разработке', show_alert=True)