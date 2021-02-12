from functions import *
from constants import *
from telegram.ext import *
from telegram import *

updater = Updater(token=TOKEN)
dispatcher = updater.dispatcher


dispatcher.add_handler(CommandHandler('start', hello_user))
dispatcher.add_handler(MessageHandler(Filters.text, get_contact))
dispatcher.add_handler(MessageHandler(Filters.contact, next_step))

updater.start_polling(clean=True)
updater.idle()
