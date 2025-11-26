#from config import *
from aiogram.types import ParseMode

from config import *

sost_1 = -1003146444014
sost_2 = -1003230906358
klan = -1003012971064
klan_chat_id = klan
token="8451829699:AAE_tfApKWq3r82i0U7yD98RCcQPIMmMT1Q"
# from telegram import Update
# from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
#
#
# async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
#
#     admins = await context.bot.getChat(chat_id=update.effective_chat.id)
#
#     print(admins)
# if __name__ == '__main__':
#     application = ApplicationBuilder().token(token).build()
#
#     start_handler = CommandHandler('start', start)
#     application.add_handler(start_handler)
#
#     application.run_polling()

bot = Bot(token=token)
dp = Dispatcher(bot)




if __name__ == "__main__":
    executor.start_polling(dp)