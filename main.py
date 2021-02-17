from constants import *
from telegram.ext import *
from telegram import *
from lib import *
import time
import logging

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


def start(update, context):
    user = update.message.from_user
    logger.info("New user started the bot. Username: %s and F_Name: %s, L_Name: %s", user.username, user.first_name,
                user.last_name)
    button = [
        [KeyboardButton("Telefon raqamni jo'natish", request_contact=True)]
    ]
    reply_markup = ReplyKeyboardMarkup(button, one_time_keyboard=True, resize_keyboard=True)
    update.message.reply_text(greeting_message, reply_markup=reply_markup)


def main_menu(update, context):
    menu_buttons = [
        [
            KeyboardButton("LACTOVITA 💊", callback_data=lactovita),
            KeyboardButton("MASSAJOR 💆‍", callback_data=massajor)
        ],
        [
            KeyboardButton("SHIFO NUR 🏥", callback_data=shifo_nur)
        ]
    ]
    reply_markup = ReplyKeyboardMarkup(menu_buttons, resize_keyboard=True)
    update.message.reply_text("Botimizdan foydalanishingiz mumkin!", reply_markup=reply_markup)


def lactovita(update, context):
    update.message.reply_text("LACTOVITA - ZOR MAHSULOT!")


def shifo_nur(update, context):
    update.message.reply_text("SHifo_NUR - ZOR JOy!")


def massajor(update, context):
    update.message.reply_text("massajor zor!")


def main():
    updater = Updater(token=TOKEN)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.contact, main_menu))
    dispatcher.add_handler(CallbackQueryHandler(callback=lactovita, pattern='lactovita'))
    dispatcher.add_handler(CallbackQueryHandler(callback=shifo_nur, pattern='shifo_nur'))
    dispatcher.add_handler(CallbackQueryHandler(callback=massajor, pattern='massajor'))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
